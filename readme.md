# templet

A minimal, elegant TUI template manager for the terminal — now with zero dependencies and smart timestamp headers.

## 📄 How it Works

**templet** lets you select pre-written templates stored in `~/Documents/templet/` and quickly copy them into your current working directory. For `.txt` and `.md` files, a timestamped header is added automatically. All other files are copied as-is.

---

## 📦 Installation

Run the install script or move the Python file manually:

```bash
chmod +x templet.py
sudo mv templet.py /usr/local/bin/templet
```

---

## 🚀 Usage

To launch the TUI interface:
```bash
templet
```

Place your templates in:
```bash
~/Documents/templet/
```

Then run `templet` inside any folder to insert a selected template.

---

## ⌨️ Keyboard Shortcuts

| Key      | Action                        |
|----------|-------------------------------|
| `↑ ↓`    | Navigate templates            |
| `Enter`  | Insert selected template      |
| `q`      | Quit the interface            |

---

## 📝 How It Stores Files

When you select a `.txt` or `.md` file, **templet** adds a header with the template name and current date/time. All other files are copied unchanged.

Example for markdown:
```md
# ✦ Template: meeting.txt
### 📅 2024-11-28 • 14:35:22
---
[your template content here]
```

---

## 📄 License

under ☕️, check out [the-coffee-license](https://github.com/codinganovel/The-Coffee-License)

I've included both licenses with the repo, do what you know is right. The licensing works by assuming your operating under good faith.

