import pytest
from airflow.models import DagBag

@pytest.fixture()
def dagbag():
    # Ensure the path points to the directory where your DAG is located.
    return DagBag(dag_folder='dags', include_examples=False)

def test_dag_import(dagbag):
    """Ensures there are no syntax errors or missing imports in the DAG file."""
    assert len(dagbag.import_errors) == 0
    assert 'weather_pipeline' in dagbag.dags

def test_dag_structure(dagbag):
    """Validates the topology, if tasks exist and are in the right order."""
    # Using .dags.get() to avoid database calls during unit testing
    dag = dagbag.dags.get('weather_pipeline')
    
    # 1. Check the existence of ALL 4 tasks
    task_ids = [task.task_id for task in dag.tasks]
    assert set(task_ids) == {'extract', 'transform', 'load', 'data_quality_check'}
    
    # 2. Get the task instances
    extract_task = dag.get_task('extract')
    transform_task = dag.get_task('transform')
    load_task = dag.get_task('load')
    dq_task = dag.get_task('data_quality_check')
    
    # 3. Check the logical order of the ETL pipeline
    assert transform_task.task_id in extract_task.downstream_task_ids
    assert load_task.task_id in transform_task.downstream_task_ids
    assert dq_task.task_id in load_task.downstream_task_ids # Validates DQ runs after load