# PKVIZ

To deploy make sure docker works and you login (`docker login`) and run:

1. Build
    ```shell
    docker build -f Dockerfile -t fgh950/dash-azure:1 .
    ```
2. Check that runs
    ```shell
    docker run -it --rm -p 4000:8080 fgh950/dash-azure:1
    ```
   Go to http://0.0.0.0:4000/ to check that it works


3. Deploy app to dockerhub
    ```shell
    docker push fgh950/dash-azure:1
    ```

https://pkpdai-search.com


### Map search query in PubMed to our api

To know how to precisely translate a filter in PubMed web interface to ours
use the following procedure:
1) Perform search in PubMed
2) Go to Advance Search under the bar
3) See the results at the bottom with the query constructed by PubMED
