FROM python:3.11

WORKDIR /app

# Install mkdocs and material theme
RUN pip install -r requirements.txt

# Copy documentation source
COPY . .

# Build the documentation to public folder
RUN mkdocs build --site-dir public

# Expose port for serving
EXPOSE 8000

# Serve the built documentation
CMD ["python", "-m", "http.server", "8000", "--directory", "public"]
