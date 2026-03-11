# EP Inspection Tool API Documentation

## Authentication Endpoints

### Login
- **Endpoint**: `POST /login`
- **Description**: Authenticate user and create session
- **Parameters**: 
  - `username` (string, required)
  - `password` (string, required)

### Logout
- **Endpoint**: `GET /logout`
- **Description**: End user session

## Inspection Endpoints

### Create Inspection
- **Endpoint**: `POST /inspections`
- **Description**: Create a new inspection report
- **Required Permissions**: authenticated user

### View Inspection
- **Endpoint**: `GET /inspections/<id>`
- **Description**: Get inspection details
- **Required Permissions**: authenticated user

### Update Inspection
- **Endpoint**: `PUT /inspections/<id>`
- **Description**: Update inspection details
- **Required Permissions**: authenticated user

### Delete Inspection
- **Endpoint**: `DELETE /inspections/<id>`
- **Description**: Delete an inspection
- **Required Permissions**: authenticated user

## Admin Endpoints

### User Management
- **Endpoint**: `GET /admin/users`
- **Description**: List all users
- **Required Permissions**: admin user

### Create User
- **Endpoint**: `POST /admin/users`
- **Description**: Create a new user
- **Required Permissions**: admin user

## File Upload Endpoints

### Upload Photo
- **Endpoint**: `POST /inspections/<id>/photos`
- **Description**: Upload a photo for an inspection
- **Required Permissions**: authenticated user

## Export Endpoints

### Export PDF
- **Endpoint**: `GET /export/inspection/<id>/pdf`
- **Description**: Export inspection as PDF
- **Required Permissions**: authenticated user