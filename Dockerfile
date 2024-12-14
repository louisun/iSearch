FROM python:3.11-alpine

WORKDIR /usr/src/iSearch
#RUN python -m pip install --upgrade pip
#RUN pip install flake8 pytest
RUN if [ -f requirements.txt ]; then pip install -r requirements.txt; fi

COPY ./ ./

RUN python -m pip install .
# RUN s 
# RUN echo 0 | s apple

ENTRYPOINT ["/usr/local/bin/s"]

#ENTRYPOINT ["tail"]
#CMD ["-f","/dev/null"]
