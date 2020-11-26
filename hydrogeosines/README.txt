Model
- Data management and storage
- Site, Data
- It consists of pure application logic, which interacts with the database. It includes all the information to and methods specific to the data.

View
- Formating / terminal output / export
- It presents the model’s data to the user.

Control/Handlers
- Data processing and logic
- It acts as an intermediary between view and model (access by user). The model is loaded into the controllers without changing the original model instance.

Ext
- Extension specific to the hgs package
- most importantly the hgs accessor for pandas which implements all the data methods unique to hgs.

Utils
- general utilities that are not specific to hgs or the model and useful anywhere in the package
