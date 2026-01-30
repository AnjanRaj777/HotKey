![HotKey Banner](assets/banner.png)

# HotKey - The Ultimate Productivity Tool

HotKey is a powerful, open-source productivity application designed to streamline your workflow on Windows. It allows you to create custom global hotkeys for launching applications, opening websites, managing windows, and executing system commands. Additionally, it features a robust text expansion engine to automate repetitive typing tasks.

Built with Python and PyQt6, HotKey offers a modern, responsive interface and runs quietly in the system tray, ensuring your tools are always just a keystroke away.

## Key Features

*   **Global Hotkeys**: Bind any key combination to trigger actions.
    *   **Run**: Launch applications or execute shell commands.
    *   **File/Folder**: Open specific files or directories instantly.
    *   **Web**: Open your favorite websites in the default browser.
    *   **Focus**: Bring specific windows to the foreground by title.
*   **Text Expansion**: Define short keywords that automatically expand into long text snippets (e.g., type "addr" to insert your full address).
*   **Modern Interface**: Clean, dark-themed UI for easy configuration.
*   **System Tray Integration**: Minimizes to the tray to keep your taskbar clutter-free.
*   **JSON Configuration**: Simple, human-readable configuration files for easy backup and sharing.
*   **Lightweight**: Minimal resource usage.

## Installation

### Prerequisites

*   Windows 10 or 11
*   Python 3.8 or higher

### Steps

1.  **Clone the Repository**

    ```bash
    git clone https://github.com/AnjanRaj777/HotKey.git
    cd HotKey
    ```

2.  **Install Dependencies**

    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the Application**

    ```bash
    python main.py
    ```

## Usage

### Managing Hotkeys

1.  Open the application from the system tray or run `main.py`.
2.  Click the **"Add Hotkey"** button.
3.  **Trigger**: Press the key combination you want to use (e.g., `Ctrl+Alt+T`).
4.  **Type**: Select the action type (`Run`, `Open File`, `Open Folder`, `Open URL`, `Focus Window`).
5.  **Target**: Enter the command, path, URL, or window title.
6.  Click **"Save"**. The hotkey is now active!

### Text Expansion

1.  Switch to the **"Text Expansion"** tab.
2.  Click **"Add Snippet"**.
3.  **Trigger**: Enter the short keyword (e.g., `:email`).
4.  **Replacement**: Enter the full text you want to expand to.
5.  Click **"Save"**.
6.  Type the trigger in any application followed by a delimiter (Space, Enter, Tab) to expand it.

## Configuration

Your settings are saved in `config.json` in the application directory. You can manually edit this file or back it up to preserve your customizations.

## Contributing

Contributions are welcome! If you have ideas for new features or improvements, please feel free to fork the repository and submit a pull request.

1.  Fork the Project
2.  Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3.  Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4.  Push to the Branch (`git push origin feature/AmazingFeature`)
5.  Open a Pull Request

## License

Distributed under the MIT License. See `LICENSE` for more information.

---

*Built with ❤️ by Anjan Raj*
