**********************
Docs Publish Workflow:
**********************

1. Optionally you can update static documentaion here, docs/source

2. To generate dynamic documentation from source-code, go back to the docs directory and generate the HTML files.
   Make sure to enter rpa spk environment to have access to sphinx.
>> cd ./docs
>> make clean; make html

3. Remove the docs/build/doctrees folder as it is not needed.
>> rm -rf ./build/doctrees

3. Copy the contents of the html folder,
>> docs/build/html

4. In another directory, clone dev-docs repo,
>> cd another/directory/to/clone/dev-docs
>> git clone git@gitlab.spimageworks.com:spi/dev/dev-ops/dev-docs.git

5. In the dev-docs repo, replace the html folder in the following path,
>> static/projects/gitprod/itview5-plugins/rpa/docs/build/html

6. Run the dev-docs server locally by running the following command from the root level of the dev-docs directory and test if everything is as expected.
>> hugo serve

7. Locally from the server, you will be able to find the RPA documentaion in the following url,
http://localhost:1313/projects/gitprod/itview5-plugins/rpa/docs/build/html/

8. You can use the following command to stop the hugo server,
>> Ctrl+C

9. If everything is as expected, create a merge request to merge the changes to dev-docs master.

10. Once the changes are merged to dev-docs master, the rpa documentaion will be live in SPI in the following link,
http://docs.spimageworks.com/projects/gitprod/itview5-plugins/rpa/docs/build/html/index.html
