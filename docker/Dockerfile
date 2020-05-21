FROM python:3.7
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt 
ENV GOOGLE_APPLICATION_CREDENTIALS="./credentials.json"
EXPOSE 8080
ENTRYPOINT [ "python" ] 
CMD [ "main.py" ] 