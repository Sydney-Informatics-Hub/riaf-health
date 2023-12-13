# Analysis Template (Python)

This is a template for a new Python analysis project that uses Quarto to create a client-accessible website.


## Setup

1. [Quarto](https://quarto.org/) needs to be installed.

2. Create and activate new conda environment for the project:

```bash
conda create -n project-env-name python==3.9

conda activate project-env-name
```

3. Record project requirements in a 'requirements.txt' and use pip to manage:

```bash
pip install -r requirements.txt
``` 

There are many options for setting up Python environments and managing dependencies, but for most situations using conda for environment management and pip for Python library management is the most easy to implement and straight foreward solution to avoid [Python environment pains](https://xkcd.com/1987/). 

## Repository File Structure

The project itself should contain the following folders:

  - 003\_literature
  - 100\_data\_cleaning\_scripts\_EDA
  - 100\_data\_raw
  - 200\_data\_clean
  - 300\_test\_data
  - 400\_analysis
  - 500\_report

You can create new folders if you need more flexibility, using 3-digit prefixes to determine where they sit in the workflow, e.g. a folder called `999_other/` would go at the end.

## Quarto Website Rendering

To render the website, execute `quarto render --to all` from the project directory. 

Don't forget to edit the following files:

- [ ] index.qmd
- [ ] about.qmd
- [ ] _quarto.yml (with your name and links to your specific project repo)

Also you will need to tick the GitHub pages to serve the site from the `main` branch, `docs` folder.

If there are other resources (e.g., Data stored elsewhere, literature stored elsewhere) that are linked to the project, they should be listed in this Readme document.

In general, data should not be uploaded to GitHub and is be excluded via the .gitignore file. A link to, or information on how to get access to the data if you have the correct permissions, must be included in the readme for the project.
