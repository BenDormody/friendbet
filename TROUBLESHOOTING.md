# Dev Container Troubleshooting Guide

## Common Issues and Solutions

### 1. Port Conflicts

**Issue**: Port 27017 is already in use by another MongoDB instance
**Solution**: The configuration now uses port 27018 for MongoDB to avoid conflicts

### 2. Docker Compose Build Failures

**Issue**: Build fails with permission or dependency errors
**Solutions**:

- Clean Docker cache: `docker system prune -a`
- Rebuild without cache: `docker-compose build --no-cache`
- Check Docker Desktop is running

### 3. Dev Container Startup Issues

**Issue**: Dev container fails to start
**Solutions**:

1. **Check Docker Desktop**: Ensure Docker Desktop is running
2. **Restart VS Code**: Close and reopen VS Code
3. **Clean up containers**:
   ```bash
   docker-compose -f .devcontainer/docker-compose.yml down
   docker system prune -f
   ```
4. **Rebuild container**: In VS Code, run "Dev Containers: Rebuild Container"

### 4. MongoDB Connection Issues

**Issue**: Application can't connect to MongoDB
**Solutions**:

- Check if MongoDB service is running: `docker ps`
- Verify connection string in `config.py`
- Ensure MongoDB port (27018) is not blocked by firewall

### 5. Permission Issues

**Issue**: Permission denied errors in container
**Solutions**:

- The Dockerfile now properly sets up user permissions
- If issues persist, try rebuilding the container

## Testing Your Setup

Run the test script to verify your configuration:

```bash
.devcontainer/test-setup.sh
```

This will check:

- Docker Compose syntax
- Port availability
- Basic configuration

## Manual Setup Alternative

If dev containers continue to fail, you can run the application manually:

1. **Install dependencies locally**:

   ```bash
   pip install -r requirements.txt
   ```

2. **Start MongoDB with Docker**:

   ```bash
   docker run -d -p 27018:27017 --name mongodb mongo:7.0
   ```

3. **Set environment variables**:

   ```bash
   export FLASK_APP=app.py
   export FLASK_ENV=development
   export MONGODB_URI=mongodb://localhost:27018/fantasy_betting
   ```

4. **Run the application**:
   ```bash
   python app.py
   ```

## Getting Help

If you continue to experience issues:

1. Check the Docker logs: `docker logs <container_name>`
2. Verify VS Code Dev Containers extension is installed
3. Ensure you have sufficient disk space
4. Try running the test script to identify specific issues

## Port Configuration

- **Flask App**: `http://localhost:5050`
- **MongoDB**: `localhost:27018`
- **Internal MongoDB**: `mongo:27017` (within container network)
