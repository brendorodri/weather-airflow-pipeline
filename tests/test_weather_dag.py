import pytest
from airflow.models import DagBag

@pytest.fixture()
def dagbag():
    # Apontando para a pasta correta da sua estrutura
    return DagBag(dag_folder='dags', include_examples=False)

def test_dag_import(dagbag):
    """Ensures there are no syntax errors or missing imports in the DAG file."""
    assert len(dagbag.import_errors) == 0
    assert 'weather_pipeline' in dagbag.dags

def test_dag_structure(dagbag):
    """Validates the topology, if tasks exist and are in the right order."""
    # Substitua .get_dag() por .dags.get()
    dag = dagbag.dags.get('weather_pipeline')
    
    # Checks the existence of the tasks
    task_ids = [task.task_id for task in dag.tasks]
    assert set(task_ids) == {'extract', 'transform', 'load'}
    
    # Gets the task instances
    extract_task = dag.get_task('extract')
    transform_task = dag.get_task('transform')
    load_task = dag.get_task('load')
    
    # Checks the logical order of the ETL (>> or set_downstream)
    assert transform_task.task_id in extract_task.downstream_task_ids
    assert load_task.task_id in transform_task.downstream_task_ids