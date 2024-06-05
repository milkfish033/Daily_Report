# Daily_report
#Sql #Python #Html #Email

***What does this project do***

This project is an advanced automated reporting system designed for the efficient monitoring and management of a knowledge base (RAG, Retrieval-Augmented Generation) system. It integrates seamlessly with a MySQL database to fetch, process, and analyze data on knowledge base entries, documents, and user interactions. By calculating daily and cumulative metrics over the past seven days, the system generates comprehensive HTML reports featuring visual trend analyses and key statistical summaries. These reports, complete with embedded graphs, provide actionable insights into the system's performance and user engagement, thereby supporting data-driven decision-making and optimizing knowledge base management.

***What will it look like when sending the html file in email***


https://github.com/milkfish033/Daily_report-/assets/141232455/2abe7b2b-fa9f-4d67-825c-5221bbed7f91



***Before you start***

***(i)Set up Virtual Environment***

***Why Virtual Environment***: Setting up a virtual environment in Python isolates project dependencies, ensuring that different projects can use different versions of the same libraries without conflicts. This isolation provides a consistent development environment, avoiding system-wide changes and simplifying dependency management.

python3 -m venv .venv && source .venv/bin/activate

***(ii)Set up Mysql***

pip install mysql-connector-python

***(iii)Set up matplotlib.pyplot***

Matplotlib.pyplot is a collection of functions that make matplotlib work like MATLAB. Each pyplot function makes some change to a figure: e.g., creates a figure, creates a plotting area in a figure, plots some lines in a plotting area, decorates the plot with labels, etc

pip install matplotlib

