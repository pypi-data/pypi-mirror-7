# Welcome to Demo Cohort

This page is written in Markdown. See the Github Markdown Guide for a good
introduction to Markdown: https://guides.github.com/features/mastering-markdown/

## Images

You may include images or other files by adding them to the `media` folder.
For example, the following image is included in the `media/images` folder
under the name 'chart.png'.

![Example chart](./media/images/chart.png)

## Attachments

You can store your files anywhere under `media` and reference them by using
a relative link (don't use absoulte links).

This is *bad*:

`[attachment]('http://example.org/media/example.pdf')`

This is *good*:

`[attachment]('./media/example.pdf')`


## Your own Page

If you are ready to create your own site from this demo, proceed as follows:

1. Create a new folder:

        mkdir my-cohort

2. Open the folder and create the initial content:

        cd my-cohort
        ocqm-cohort-website init

3. Change the content to your liking and serve the result under http://127.0.0.1:8000

        ocqm-cohort-website build --serve

4. To build the site without showing it use:

        ocqm-cohort-website build

You will find the result of the build in the `my-cohort/output` folder. This
folder is ready to be served by a webserver.

To use an alternative output folder you can run:

    ocqm-cohort-website build --output my/other/folder


## Development

ocqm_cohort_website is open source. Development happens on Github:
https://github.com/seantis/ocqm_cohort_website
