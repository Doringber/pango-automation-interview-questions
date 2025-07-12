import os

from ..utilities.data_population import populate_db

def test_pipeline():
    populate_db()
    assert os.path.exists("data.db"), 'Failed to find data.db (database) file.'
    assert os.path.exists("reports/report.md"), 'Failed to find report file.'

