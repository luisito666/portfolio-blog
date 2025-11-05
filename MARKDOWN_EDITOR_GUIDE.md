# Markdown Editor for Django Admin

This markdown editor has been added to your Django admin panel to help you format blog posts more easily.

## Available Features

The markdown editor includes the following formatting buttons:

### Text Formatting
- **Bold** (`Ctrl+B`): Makes text bold
- **Italic** (`Ctrl+I`): Makes text italic  
- **Heading** (`Ctrl+H`): Creates heading with # character
- **Center**: Centers text using HTML center tags

### Links and Media
- **Link** (`Ctrl+L`): Creates hyperlinks, prompts for URL
- **Image** (`Ctrl+Shift+I`): Adds images, prompts for URL and alt text

### Code Formatting
- **Code** (`Ctrl+Shift+C`): Inline code with backticks
- **Code Block** (`Ctrl+Shift+B`): Multi-line code blocks

### Lists and Structure
- **Quote** (`Ctrl+Shift+Q`): Blockquotes with > character
- **Unordered List** (`Ctrl+U`): Bullet points with - character
- **Ordered List** (`Ctrl+Shift+O`): Numbered lists
- **Horizontal Rule** (`Ctrl+R`): Horizontal divider with --- 

## How to Use

1. **Access the Admin**: Go to `/admin/blog/blogpost/` in your browser
2. **Create/Edit Post**: Click on a post or add a new one
3. **Use the Toolbar**: You'll see a toolbar with all the formatting buttons above the content field
4. **Keyboard Shortcuts**: Use Ctrl+letter combinations for quick formatting (see shortcuts above)

## Example Markdown Syntax

### Basic Text
- `**bold text**` → **bold text**
- `*italic text*` → *italic text*
- `# Heading 1` → Heading 1

### Links and Images
- `[Link Text](https://example.com)` → [Link Text](https://example.com)
- `![Image Alt Text](https://example.com/image.jpg)`

### Lists
```
- Item 1
- Item 2

1. First
2. Second
```

### Code
- `` `inline code` `` → `inline code`
- ```python
  # Code block
  print("Hello World")
  ```

## Features Added

✅ Custom markdown toolbar with 12 formatting buttons
✅ Keyboard shortcuts for common formatting
✅ Responsive design for mobile devices
✅ Visual feedback and hover effects
✅ Markdown help text below the editor
✅ Support for both content and excerpt fields

## Files Modified

- `apps/blog/admin_widgets.py`: Custom markdown widgets
- `apps/blog/admin.py`: Updated admin configuration
- `apps/blog/static/admin/js/markdown_editor.js`: JavaScript functionality
- `apps/blog/static/admin/css/markdown_editor.css`: Styling
- `blog_penny/settings.py`: Static files configuration

## Usage Tips

1. **Select text first**: Select the text you want to format, then click a button
2. **No selection needed**: If no text is selected, the button will insert template text
3. **Keyboard shortcuts**: Use Ctrl+letter combinations for faster editing
4. **HTML support**: You can use HTML tags in markdown for special formatting like `<center>`

The editor will help you create well-formatted blog posts with proper markdown syntax!