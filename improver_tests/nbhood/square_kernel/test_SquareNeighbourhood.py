# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# (C) British Crown Copyright 2017-2020 Met Office.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# * Neither the name of the copyright holder nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
"""Unit tests for the nbhood.square_kernel.SquareNeighbourhood plugin."""


import unittest

import iris
import numpy as np
from iris.coords import CellMethod, DimCoord
from iris.cube import Cube
from iris.tests import IrisTest

from improver.nbhood.square_kernel import SquareNeighbourhood
from improver.wind_calculations.wind_direction import WindDirection

from ..nbhood.test_BaseNeighbourhoodProcessing import set_up_cube


class Test__init__(IrisTest):

    """Test the init method."""

    def test_sum_or_fraction(self):
        """Test that a ValueError is raised if an invalid option is passed
        in for sum_or_fraction."""
        sum_or_fraction = "nonsense"
        msg = "option is invalid"
        with self.assertRaisesRegex(ValueError, msg):
            SquareNeighbourhood(sum_or_fraction=sum_or_fraction)


class Test__repr__(IrisTest):

    """Test the repr method."""

    def test_basic(self):
        """Test that the __repr__ returns the expected string."""
        result = str(SquareNeighbourhood())
        msg = (
            "<SquareNeighbourhood: weighted_mode: {}, "
            "sum_or_fraction: {}, re_mask: {}>".format(True, "fraction", True)
        )
        self.assertEqual(result, msg)


class Test_run(IrisTest):

    """Test the run method on the SquareNeighbourhood class."""

    RADIUS = 2500

    def test_basic_re_mask_true(self):
        """Test that a cube with correct data is produced by the run method
        when re-masking is applied."""
        data = np.array(
            [
                [
                    [
                        [1.0, 1.0, 1.0, 1.0, 1.0],
                        [1.0, 0.88888889, 0.88888889, 0.88888889, 1.0],
                        [1.0, 0.88888889, 0.88888889, 0.88888889, 1.0],
                        [1.0, 0.88888889, 0.88888889, 0.88888889, 1.0],
                        [1.0, 1.0, 1.0, 1.0, 1.0],
                    ]
                ]
            ]
        )
        cube = set_up_cube(
            zero_point_indices=((0, 0, 2, 2),), num_time_points=1, num_grid_points=5
        )
        result = SquareNeighbourhood().run(cube, self.RADIUS)
        self.assertIsInstance(cube, Cube)
        self.assertArrayAlmostEqual(result.data, data)

    def test_negative_strides_re_mask_true(self):
        """Test that a cube still works if there are negative-strides."""
        data = np.array(
            [
                [
                    [
                        [1.0, 1.0, 1.0, 1.0, 1.0],
                        [1.0, 0.88888889, 0.88888889, 0.88888889, 1.0],
                        [1.0, 0.88888889, 0.88888889, 0.88888889, 1.0],
                        [1.0, 0.88888889, 0.88888889, 0.88888889, 1.0],
                        [1.0, 1.0, 1.0, 1.0, 1.0],
                    ]
                ]
            ]
        )
        cube = set_up_cube(
            zero_point_indices=((0, 0, 2, 2),), num_time_points=1, num_grid_points=5
        )
        coord_points_x = np.arange(-42000, -52000.0, -2000)
        coord_points_y = np.arange(8000.0, -2000, -2000)

        cube.coord("projection_x_coordinate").points = coord_points_x
        cube.coord("projection_y_coordinate").points = coord_points_y

        result = SquareNeighbourhood().run(cube, self.RADIUS)
        self.assertIsInstance(cube, Cube)
        self.assertArrayAlmostEqual(result.data, data)

    def test_basic_re_mask_false(self):
        """Test that a cube with correct data is produced by the run method."""
        data = np.array(
            [
                [
                    [
                        [1.0, 1.0, 1.0, 1.0, 1.0],
                        [1.0, 0.88888889, 0.88888889, 0.88888889, 1.0],
                        [1.0, 0.88888889, 0.88888889, 0.88888889, 1.0],
                        [1.0, 0.88888889, 0.88888889, 0.88888889, 1.0],
                        [1.0, 1.0, 1.0, 1.0, 1.0],
                    ]
                ]
            ]
        )
        cube = set_up_cube(
            zero_point_indices=((0, 0, 2, 2),), num_time_points=1, num_grid_points=5
        )
        result = SquareNeighbourhood(re_mask=False).run(cube, self.RADIUS)
        self.assertIsInstance(cube, Cube)
        self.assertArrayAlmostEqual(result.data, data)

    def test_masked_array_re_mask_true(self):
        """Test that the run method produces a cube with correct data when a
        cube containing masked data is passed in and re-masking is applied."""
        cube = set_up_cube(
            zero_point_indices=((0, 0, 2, 2),), num_time_points=1, num_grid_points=5
        )
        cube.data = np.array(
            [
                [
                    [
                        [1, 1, 0, 1, 1],
                        [1, 1, 1, 0, 0],
                        [1, 0, 1, 0, 0],
                        [0, 0, 1, 1, 0],
                        [0, 1, 1, 0, 1],
                    ]
                ]
            ]
        )
        mask = np.array(
            [
                [
                    [
                        [0, 0, 1, 1, 0],
                        [0, 1, 1, 1, 0],
                        [0, 0, 1, 1, 1],
                        [0, 0, 1, 1, 0],
                        [0, 0, 1, 1, 0],
                    ]
                ]
            ]
        )
        expected_array = np.array(
            [
                [
                    [
                        [1.0000, 0.666667, 0.600000, 0.500000, 0.50],
                        [1.0000, 0.750000, 0.571429, 0.428571, 0.25],
                        [1.0000, 1.000000, 0.714286, 0.571429, 0.25],
                        [np.nan, 1.000000, 0.666667, 0.571429, 0.25],
                        [np.nan, 1.000000, 0.750000, 0.750000, 0.50],
                    ]
                ]
            ]
        )
        expected_mask_array = np.array(
            [
                [
                    [
                        [True, True, False, False, True],
                        [True, False, False, False, True],
                        [True, True, False, False, False],
                        [True, True, False, False, True],
                        [True, True, False, False, True],
                    ]
                ]
            ]
        )
        cube.data = np.ma.masked_where(mask == 0, cube.data)
        result = SquareNeighbourhood().run(cube, self.RADIUS)
        self.assertArrayAlmostEqual(result.data.data, expected_array)
        self.assertArrayAlmostEqual(result.data.mask, expected_mask_array)

    def test_masked_array_re_mask_false(self):
        """Test that the run method produces a cube with correct data when a
           cube containing masked data is passed in."""
        cube = set_up_cube(
            zero_point_indices=((0, 0, 2, 2),), num_time_points=1, num_grid_points=5
        )
        cube.data = np.array(
            [
                [
                    [
                        [1, 1, 0, 1, 1],
                        [1, 1, 1, 0, 0],
                        [1, 0, 1, 0, 0],
                        [0, 0, 1, 1, 0],
                        [0, 1, 1, 0, 1],
                    ]
                ]
            ]
        )
        mask = np.array(
            [
                [
                    [
                        [0, 0, 1, 1, 0],
                        [0, 1, 1, 1, 0],
                        [0, 0, 1, 1, 1],
                        [0, 0, 1, 1, 0],
                        [0, 0, 1, 1, 0],
                    ]
                ]
            ]
        )
        expected_array = np.array(
            [
                [
                    [
                        [1.0000, 0.666667, 0.600000, 0.500000, 0.50],
                        [1.0000, 0.750000, 0.571429, 0.428571, 0.25],
                        [1.0000, 1.000000, 0.714286, 0.571429, 0.25],
                        [np.nan, 1.000000, 0.666667, 0.571429, 0.25],
                        [np.nan, 1.000000, 0.750000, 0.750000, 0.50],
                    ]
                ]
            ]
        )
        cube.data = np.ma.masked_where(mask == 0, cube.data)
        result = SquareNeighbourhood(re_mask=False).run(cube, self.RADIUS)
        self.assertArrayAlmostEqual(result.data, expected_array)

    def test_nan_array_re_mask_true(self):
        """Test that an array containing nans is handled correctly when
        re-masking is applied."""
        data = np.array(
            [
                [
                    [
                        [np.nan, 1.0, 1.0, 1.0, 1.0],
                        [1.0, 0.8750000, 0.88888889, 0.88888889, 1.0],
                        [1.0, 0.88888889, 0.88888889, 0.88888889, 1.0],
                        [1.0, 0.88888889, 0.88888889, 0.88888889, 1.0],
                        [1.0, 1.0, 1.0, 1.0, 1.0],
                    ]
                ]
            ]
        )
        cube = set_up_cube(
            zero_point_indices=((0, 0, 2, 2),), num_time_points=1, num_grid_points=5
        )
        cube.data[0, 0, 0, 0] = np.nan
        result = SquareNeighbourhood().run(cube, self.RADIUS)
        self.assertIsInstance(result, Cube)
        self.assertArrayAlmostEqual(result.data, data)

    def test_nan_array_re_mask_false(self):
        """Test that an array containing nans is handled correctly."""
        data = np.array(
            [
                [
                    [
                        [np.nan, 1.0, 1.0, 1.0, 1.0],
                        [1.0, 0.8750000, 0.88888889, 0.88888889, 1.0],
                        [1.0, 0.88888889, 0.88888889, 0.88888889, 1.0],
                        [1.0, 0.88888889, 0.88888889, 0.88888889, 1.0],
                        [1.0, 1.0, 1.0, 1.0, 1.0],
                    ]
                ]
            ]
        )
        cube = set_up_cube(
            zero_point_indices=((0, 0, 2, 2),), num_time_points=1, num_grid_points=5
        )
        cube.data[0, 0, 0, 0] = np.nan
        result = SquareNeighbourhood(re_mask=False).run(cube, self.RADIUS)
        self.assertIsInstance(cube, Cube)
        self.assertArrayAlmostEqual(result.data, data)

    def test_masked_array_with_nans_re_mask_true(self):
        """Test that the run method produces a cube with correct data when a
        cube containing masked nans is passed in and when re-masking is
        applied."""
        cube = set_up_cube(
            zero_point_indices=((0, 0, 2, 2),), num_time_points=1, num_grid_points=5
        )
        cube.data = np.array(
            [
                [
                    [
                        [np.nan, 1, 0, 1, 1],
                        [1, 1, 1, 0, 0],
                        [1, 0, 1, 0, 0],
                        [0, 0, 1, 1, 0],
                        [0, 1, 1, 0, 1],
                    ]
                ]
            ]
        )
        mask = np.array(
            [
                [
                    [
                        [0, 0, 1, 1, 0],
                        [0, 1, 1, 1, 0],
                        [0, 0, 1, 1, 1],
                        [0, 0, 1, 1, 0],
                        [0, 0, 1, 1, 0],
                    ]
                ]
            ]
        )
        expected_array = np.array(
            [
                [
                    [
                        [np.nan, 0.666667, 0.600000, 0.500000, 0.50],
                        [1.0000, 0.750000, 0.571429, 0.428571, 0.25],
                        [1.0000, 1.000000, 0.714286, 0.571429, 0.25],
                        [np.nan, 1.000000, 0.666667, 0.571429, 0.25],
                        [np.nan, 1.000000, 0.750000, 0.750000, 0.50],
                    ]
                ]
            ]
        )
        cube.data = np.ma.masked_where(mask == 0, cube.data)
        result = SquareNeighbourhood().run(cube, self.RADIUS)
        self.assertArrayAlmostEqual(result.data, expected_array)

    def test_masked_array_with_nans_re_mask_false(self):
        """Test that the run method produces a cube with correct data when a
           cube containing masked nans is passed in."""
        cube = set_up_cube(
            zero_point_indices=((0, 0, 2, 2),), num_time_points=1, num_grid_points=5
        )
        cube.data = np.array(
            [
                [
                    [
                        [np.nan, 1, 0, 1, 1],
                        [1, 1, 1, 0, 0],
                        [1, 0, 1, 0, 0],
                        [0, 0, 1, 1, 0],
                        [0, 1, 1, 0, 1],
                    ]
                ]
            ]
        )
        mask = np.array(
            [
                [
                    [
                        [0, 0, 1, 1, 0],
                        [0, 1, 1, 1, 0],
                        [0, 0, 1, 1, 1],
                        [0, 0, 1, 1, 0],
                        [0, 0, 1, 1, 0],
                    ]
                ]
            ]
        )
        expected_array = np.array(
            [
                [
                    [
                        [np.nan, 0.666667, 0.600000, 0.500000, 0.50],
                        [1.0000, 0.750000, 0.571429, 0.428571, 0.25],
                        [1.0000, 1.000000, 0.714286, 0.571429, 0.25],
                        [np.nan, 1.000000, 0.666667, 0.571429, 0.25],
                        [np.nan, 1.000000, 0.750000, 0.750000, 0.50],
                    ]
                ]
            ]
        )
        cube.data = np.ma.masked_where(mask == 0, cube.data)
        result = SquareNeighbourhood(re_mask=False).run(cube, self.RADIUS)
        self.assertArrayAlmostEqual(result.data, expected_array)

    def test_complex(self):
        """Test that a cube containing complex numbers is sensibly processed"""
        cube = set_up_cube(
            zero_point_indices=((0, 0, 2, 2),), num_time_points=1, num_grid_points=5
        )
        cube.data = cube.data.astype(complex)
        cube.data[0, 0, 1, 3] = 0.5 + 0.5j
        cube.data[0, 0, 4, 3] = 0.4 + 0.6j
        expected_data = np.array(
            [
                [
                    [
                        [
                            1.0 + 0.0j,
                            1.0 + 0.0j,
                            0.91666667 + 0.083333333j,
                            0.91666667 + 0.083333333j,
                            0.875 + 0.125j,
                        ],
                        [
                            1.0 + 0.0j,
                            0.88888889 + 0.0j,
                            0.83333333 + 0.055555556j,
                            0.83333333 + 0.055555556j,
                            0.91666667 + 0.083333333j,
                        ],
                        [
                            1.0 + 0.0j,
                            0.88888889 + 0.0j,
                            0.83333333 + 0.055555556j,
                            0.83333333 + 0.055555556j,
                            0.91666667 + 0.083333333j,
                        ],
                        [
                            1.0 + 0.0j,
                            0.88888889 + 0.0j,
                            0.82222222 + 0.066666667j,
                            0.82222222 + 0.066666667j,
                            0.9 + 0.1j,
                        ],
                        [1.0 + 0.0j, 1.0 + 0.0j, 0.9 + 0.1j, 0.9 + 0.1j, 0.85 + 0.15j],
                    ]
                ]
            ]
        )
        result = SquareNeighbourhood().run(cube, self.RADIUS)
        self.assertArrayAlmostEqual(result.data, expected_data)

    def test_multiple_times(self):
        """Test that a cube with correct data is produced by the run method
        when multiple times are supplied."""
        expected_1 = np.array(
            [
                [1.0, 1.0, 1.0, 1.0, 1.0],
                [1.0, 0.88888889, 0.88888889, 0.88888889, 1.0],
                [1.0, 0.88888889, 0.88888889, 0.88888889, 1.0],
                [1.0, 0.88888889, 0.88888889, 0.88888889, 1.0],
                [1.0, 1.0, 1.0, 1.0, 1.0],
            ]
        )
        expected_2 = np.array(
            [
                [1.0, 0.83333333, 0.83333333, 0.83333333, 1.0],
                [1.0, 0.88888889, 0.88888889, 0.88888889, 1.0],
                [1.0, 0.88888889, 0.88888889, 0.88888889, 1.0],
                [1.0, 1.0, 1.0, 1.0, 1.0],
                [1.0, 1.0, 1.0, 1.0, 1.0],
            ]
        )
        cube = set_up_cube(
            zero_point_indices=((0, 0, 2, 2), (0, 1, 1, 2)),
            num_time_points=2,
            num_grid_points=5,
        )
        result = SquareNeighbourhood().run(cube, self.RADIUS)
        self.assertIsInstance(cube, Cube)
        self.assertArrayAlmostEqual(result.data[0, 0], expected_1)
        self.assertArrayAlmostEqual(result.data[0, 1], expected_2)

    def test_multiple_times_with_mask(self):
        """Test that the run method produces a cube with correct data when a
        cube containing masked data at multiple time steps is passed in.
        Re-masking is disabled."""
        cube = set_up_cube(
            zero_point_indices=((0, 0, 2, 2),), num_time_points=2, num_grid_points=5
        )
        data = np.array(
            [
                [
                    [
                        [1, 1, 0, 1, 1],
                        [1, 1, 1, 0, 0],
                        [1, 0, 1, 0, 0],
                        [0, 0, 1, 1, 0],
                        [0, 1, 1, 0, 1],
                    ],
                    [
                        [1, 1, 0, 1, 1],
                        [1, 1, 1, 0, 0],
                        [1, 0, 1, 0, 0],
                        [0, 0, 1, 0, 0],
                        [0, 1, 1, 0, 1],
                    ],
                ]
            ]
        )
        mask = np.array(
            [
                [
                    [
                        [0, 0, 1, 1, 0],
                        [0, 1, 1, 1, 0],
                        [0, 0, 1, 1, 1],
                        [0, 0, 1, 1, 0],
                        [0, 0, 1, 1, 0],
                    ],
                    [
                        [0, 0, 1, 1, 0],
                        [0, 1, 1, 1, 0],
                        [0, 1, 1, 1, 1],
                        [0, 0, 0, 1, 0],
                        [0, 0, 1, 1, 0],
                    ],
                ]
            ]
        )
        masked_data = np.ma.masked_where(mask == 0, data)
        cube.data = masked_data
        expected_array = np.array(
            [
                [
                    [
                        [1.0000, 0.666667, 0.600000, 0.500000, 0.500000],
                        [1.0000, 0.750000, 0.571429, 0.428571, 0.250000],
                        [1.0000, 1.000000, 0.714286, 0.571429, 0.250000],
                        [np.nan, 1.000000, 0.666667, 0.571429, 0.250000],
                        [np.nan, 1.000000, 0.750000, 0.750000, 0.500000],
                    ],
                    [
                        [1.0000, 0.666667, 0.600000, 0.500000, 0.500000],
                        [0.5000, 0.600000, 0.500000, 0.428571, 0.250000],
                        [0.5000, 0.750000, 0.428571, 0.333333, 0.000000],
                        [0.0000, 0.666667, 0.333333, 0.333333, 0.000000],
                        [np.nan, 1.000000, 0.333333, 0.333333, 0.000000],
                    ],
                ]
            ]
        )
        result = SquareNeighbourhood(re_mask=False).run(cube, self.RADIUS)
        self.assertArrayAlmostEqual(result.data, expected_array)

    def test_multiple_times_nan(self):
        """Test that a cube with correct data is produced by the run method
        for multiple times and for when nans are present."""
        expected_1 = np.array(
            [
                [np.nan, 0.8, 0.8333333, 0.8333333, 1.0],
                [1.0, 0.75, 0.77777778, 0.77777778, 1.0],
                [1.0, 0.77777778, 0.77777778, 0.77777778, 1.0],
                [1.0, 0.88888889, 0.88888889, 0.88888889, 1.0],
                [1.0, 1.0, 1.0, 1.0, 1.0],
            ]
        )
        expected_2 = np.array(
            [
                [1.0, 1.0, 1.0, 1.0, 1.0],
                [1.0, np.nan, 1.0, 1.0, 1.0],
                [1.0, 1.0, 1.0, 1.0, 1.0],
                [1.0, 1.0, 1.0, 1.0, 1.0],
                [1.0, 1.0, 1.0, 1.0, 1.0],
            ]
        )
        cube = set_up_cube(
            zero_point_indices=((0, 0, 2, 2), (0, 0, 1, 2)),
            num_time_points=2,
            num_grid_points=5,
        )
        cube.data[0, 0, 0, 0] = np.nan
        cube.data[0, 1, 1, 1] = np.nan
        result = SquareNeighbourhood().run(cube, self.RADIUS)
        self.assertIsInstance(cube, Cube)
        self.assertArrayAlmostEqual(result.data[0, 0], expected_1)
        self.assertArrayAlmostEqual(result.data[0, 1], expected_2)

    def test_metadata(self):
        """Test that a cube with correct metadata is produced by the run
        method."""
        cube = set_up_cube(
            zero_point_indices=((0, 0, 2, 2),), num_time_points=1, num_grid_points=5
        )
        cube.attributes = {"Conventions": "CF-1.5"}
        cube.add_cell_method(CellMethod("mean", coords="time"))
        result = SquareNeighbourhood().run(cube, self.RADIUS)
        self.assertIsInstance(cube, Cube)
        self.assertTupleEqual(result.cell_methods, cube.cell_methods)
        self.assertDictEqual(result.attributes, cube.attributes)


if __name__ == "__main__":
    unittest.main()
