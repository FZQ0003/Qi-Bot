# From salaxieb/perlin_noise

import pickle
from typing import Tuple, Union, List, Optional

import numpy as np
from numpy.random import Generator, SeedSequence, PCG64DXSM

from .hash import hash_encode
from .logger import logger
from .model import QiModel

TYPE_SIZE = Union[Tuple[int, ...], List[int], np.ndarray]


def _random(entropy, spawn_key):
    rng = Generator(PCG64DXSM(SeedSequence(entropy, spawn_key=spawn_key)))  # noqa
    vec = rng.normal(size=len(spawn_key))
    return vec / np.linalg.norm(vec)


_np_random = np.vectorize(_random, excluded=['entropy', 0], signature='(n)->(n)')


def _rand_vec(seed, grids):
    # Grid vectors: shape = (dim, <size*dim>)
    # Random vectors: n-dim rand array
    return _np_random(seed, np.mgrid[map(slice, grids)].T).T


def _fade(x):
    return x ** 3 * (6 * x ** 2 - 15 * x + 10)


class PerlinNoiseState(QiModel):
    grids: np.ndarray
    grid_size: np.ndarray
    rand_vec: np.ndarray
    delta_box: np.ndarray
    blend_weight: np.ndarray


class PerlinNoiseCache(QiModel):
    coordinates: np.ndarray
    distance: np.ndarray
    coord_rand: np.ndarray
    weight: np.ndarray


class PerlinNoise(object):

    def __init__(self,
                 size: TYPE_SIZE = (100, 100),
                 scale: float = 1.0,
                 detail: int = 2,
                 blend: float = 0.5,
                 seed=None,
                 init_state: PerlinNoiseState = None):
        # Cache
        self.cache: Optional[PerlinNoiseState] = None
        # Fast init from another class
        if init_state:
            self._size = size
            self._seed = seed
            self.state = init_state
            return
        # Parse params and write to attribute
        size = self._parse_size(size)
        scale = self._parse_scale(scale)
        detail = self._parse_detail(detail)
        blend = self._parse_blend(blend)
        seed = self._parse_seed(seed)

        # Generate grids of random vectors
        max_grid_size = max(size) / scale / 2 ** (detail - 1)
        # Amount of grids
        grids = np.ceil(size / max_grid_size).astype(int) + 1
        # grids = tuple(math.ceil(_ / max_grid_size) + 1 for _ in size)
        # Random vectors, n-dim rand array
        rand_vec = _rand_vec(seed, grids)

        # Dimension (n)
        dim = len(size)
        # Temp list that describes dim to reshape
        _l_dim = [1] * dim
        # Grid size (for FBM)
        # shape = (1, 1, detail, <1*dim>)
        grid_size = max_grid_size * 2 ** np.arange(detail)[::-1].reshape([1, 1, -1] + _l_dim)

        # Combination of 0 & 1
        # shape = (dim, 2^dim, 1, <1*dim>)
        delta_box = np.mgrid[[slice(2)] * dim].reshape([dim, -1, 1] + _l_dim)

        # Blend
        blend_weight = 0.5 ** np.arange(detail).reshape([-1] + _l_dim) * blend
        blend_weight[0] = 1

        # Write to state
        self.state = PerlinNoiseState(
            grids=grids,
            grid_size=grid_size,
            rand_vec=rand_vec,
            delta_box=delta_box,
            blend_weight=blend_weight
        )
        self._size = size
        self._seed = seed

    @staticmethod
    def _parse_size(size: TYPE_SIZE) -> np.ndarray:
        for x in size:
            if type(x) is not int or x < 1:
                raise ValueError(f'Incorrect size: {x}.')
        return np.array(size)

    @property
    def size(self) -> Tuple[int, ...]:
        return tuple(self._size)

    @staticmethod
    def _parse_scale(scale: float) -> float:
        if not 0.01 <= scale <= 100:
            scale = np.clip(abs(scale), 0.01, 100)
            logger.warning(f'Set scale to {scale}.')
        return scale

    @property
    def scale(self) -> float:
        return max(self._size) / self.state.grid_size[0]

    @staticmethod
    def _parse_detail(detail: int) -> int:
        if type(detail) is not int or detail < 1:
            detail = min(int(detail), 1)
            logger.warning(f'Set detail to {detail}.')
        return detail

    @property
    def detail(self) -> int:
        # return self.state.grid_size.shape[2]
        return len(self.state.blend_weight)

    @staticmethod
    def _parse_blend(blend: float) -> float:
        if not 0 <= blend <= 1:
            blend = np.clip(blend, 0, 1)
            logger.warning(f'Set blend to {blend}.')
        return blend

    @property
    def blend(self) -> float:
        return self.state.blend_weight[1] * 2

    @staticmethod
    def _parse_seed(seed=None, force_encode: bool = True) -> int:
        if seed is None:
            seed = SeedSequence().entropy
        elif type(seed) is int and not force_encode:
            pass
        else:
            seed = int.from_bytes(hash_encode(pickle.dumps(seed), return_bytes=True), 'big')
        logger.info(f'Set actual seed to {seed}.')
        return seed

    @property
    def seed(self) -> int:
        return self._seed

    def reseed(self, seed) -> 'PerlinNoise':
        seed = self._parse_seed(seed)
        return self.__class__(
            size=self._size,
            seed=seed,
            init_state=self.state.copy(
                update={
                    'rand_vec': _rand_vec(seed, self.state.grids)
                }
            )
        )

    @property
    def dim(self) -> int:
        return len(self.state.grids)

    def generate_all(self, step: Union[List[int], int] = 1) -> np.ndarray:
        if type(step) is int:
            step = [step]
        index = map(
            lambda x, y: slice(0, x, y),
            self._size,
            np.array(step)[np.arange(self.dim) % len(step)]
        )
        return self.generate(np.mgrid[index])

    def generate(self,
                 input_element: np.ndarray = None,
                 order: str = 'F',
                 repeat: bool = False) -> np.ndarray:
        if input_element is None:
            input_element = np.mgrid[map(slice, self._size)]
            order = 'F'
        elif order == 'C':
            input_element = input_element.T
        # Input coordinates (add dim to repeat)
        # shape = (dim, 1, detail, <size*dim>)
        coordinates = input_element[:, None, None] / self.state.grid_size
        # Generate bounding box (repeat for final sum)
        # shape = (dim, 2^dim, detail, <size*dim>)
        coord_bounding_box = (coordinates // 1).astype(int) + self.state.delta_box
        # Distance vectors
        distance = coordinates - coord_bounding_box

        # Index rand vectors
        if repeat:
            coord_bounding_box %= self.state.grids.reshape([-1, 1, 1] + [1] * self.dim)
        coord_rand = self.state.rand_vec[tuple([...] + list(coord_bounding_box))]
        # Calculate weights
        # shape = (2^dim, detail, <size*dim>)
        weight = np.prod(_fade(1 - np.abs(distance)), axis=0) * np.sum(coord_rand * distance, axis=0)

        # Calculate sum
        out = np.sum(np.sum(weight, axis=0) * self.state.blend_weight, axis=0)
        # Write cache
        self.cache = PerlinNoiseCache(
            coordinates=coordinates,
            distance=distance,
            coord_rand=coord_rand,
            weight=weight
        )
        # Output
        if order == 'C':
            return out.T
        return out
