
import unittest
from unittest.mock import patch

import pandas as pd

from src import pipeline


class TestRetailSalesPipeline(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Load the source dataset once for the test suite."""
        cls.raw_data = pipeline.extract_data()

    def test_extract_data(self):
        """Check that extraction loads the expected records."""
        self.assertEqual(len(self.raw_data), 9994)
        self.assertFalse(self.raw_data.empty)

    def test_transform_data(self):
        """Check that transformation cleans and validates the data."""
        clean_data = pipeline.transform_data(self.raw_data)

        self.assertEqual(len(clean_data), 9994)

        self.assertTrue(
            pd.api.types.is_datetime64_any_dtype(
                clean_data["Order Date"]
            )
        )

        self.assertTrue(
            pd.api.types.is_datetime64_any_dtype(
                clean_data["Ship Date"]
            )
        )

        self.assertFalse(clean_data.duplicated().any())

    def test_invalid_quantity_is_rejected(self):
        """Check that invalid quantities cause validation to fail."""
        sample = self.raw_data.head(1).copy()
        sample.loc[sample.index[0], "Quantity"] = 0

        with self.assertRaises(ValueError):
            pipeline.transform_data(sample)

    def test_load_data(self):
        """Check that data is loaded into SQLite successfully."""
        clean_data = pipeline.transform_data(
            self.raw_data.head(10)
        )

        # Use an in-memory SQLite database for this test
        with patch.object(
            pipeline, "DATABASE_FILE", ":memory:"
        ):
            loaded_rows = pipeline.load_data(clean_data)

        self.assertEqual(loaded_rows, 10)


if __name__ == "__main__":
    unittest.main()
