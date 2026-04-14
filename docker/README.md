# Docker Setup for Phoenix

## Build

```bash
cd docker
docker build -t phoenix .
```

## Run

Mount your code directory and model weights:

```bash
docker run --gpus all -it \
    -v $(pwd)/..:/workspace \
    -v /path/to/your/models:/workspace/models \
    phoenix
```

Inside the container, activate the environment and run the pipeline:

```bash
conda activate phoenix
cd /workspace
bash pipelines/run_full_pipeline.sh
```
