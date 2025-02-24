<div align="center">

# WSL Manager v2

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.6%2B-blue.svg)](https://www.python.org/)
[![Windows](https://img.shields.io/badge/Platform-Windows-blue.svg)](https://www.microsoft.com/windows)

_A powerful graphical interface for managing Windows Subsystem for Linux (WSL) distributions_

Developed by [GUIRATEC](https://github.com/GUIRATEC)

</div>

## 🚀 About

WSL Manager is an Open Source software designed and created by Franklin Gutierrez, CEO and founder of GUIRATEC. This application provides a user-friendly graphical interface for managing Linux subsystems (WSL) directly in Windows, eliminating the need for virtual machines or dual boot setups. WSL Manager enables seamless integration between Windows and Linux, allowing users to leverage tools and applications from both operating systems simultaneously.

![image](https://github.com/user-attachments/assets/026f39c7-cd96-4b75-8b76-4a96a338622c)


## ✨ Features

- 🔄 **Easy Distribution Management**

  - Install new WSL distributions
  - Execute existing distributions
  - Move distributions between locations
  - Delete unwanted distributions

- 📦 **Distribution Backup & Restore**

  - Export distributions to backup files
  - Import distributions from local backup files
  - Manage backup locations

- 🛠 **User-Friendly Interface**
  - Dark mode interface
  - Intuitive tab-based navigation
  - Clear status messages and confirmations
  - Simple configuration management

## 📋 Requirements

- Windows 10 version 2004 and higher (Build 19041 and higher) or Windows 11
- Windows Subsystem for Linux (WSL) enabled
- Python 3.6 or higher
- Required Python packages (see requirements.txt)

## 🔧 Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/GUIRATEC/wsl_admin.git
   ```

2. Navigate to the project directory:

   ```bash
   cd wsl_admin
   ```

3. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## 💻 Usage

1. Run the application:

   ```bash
   python wsl_manager.py
   ```

2. Use the tabs to access different functions:
   - **Configuration**: Set up export and import paths
   - **Install Distro**: Install new WSL distributions
   - **Execute Distro**: Launch installed distributions
   - **Move Distro**: Relocate distributions to different paths
   - **Move Distro from Local File**: Import distributions from backup files
   - **Delete Distro**: Remove unwanted distributions

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! Feel free to check the [issues page](https://github.com/GUIRATEC/wsl_admin/issues).

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👨‍💻 Author

**Franklin Gutierrez**

- CEO & Founder of GUIRATEC
- Web: [@GUIRATEC](https://guiratec.com/)

---

<div align="center">

Made with ❤️ by [Franklin Gutierrez](https://github.com/franklingutierrez)

</div>
