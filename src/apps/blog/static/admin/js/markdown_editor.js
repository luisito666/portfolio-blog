// Markdown Editor JavaScript for Django Admin - Production Version

(function() {
    'use strict';

    class MarkdownEditor {
        constructor(textarea) {
            this.textarea = textarea;
            this.toolbar = null;
            this.container = null;
            this.init();
        }

        init() {
            this.createToolbar();
            this.bindEvents();
        }

        createToolbar() {
            // Create container wrapper
            this.container = document.createElement('div');
            this.container.className = 'markdown-toolbar-container';
            this.container.id = `container-${this.textarea.id}`;
            
            // Create toolbar
            const toolbar = document.createElement('div');
            toolbar.className = 'markdown-toolbar';
            toolbar.id = `toolbar-${this.textarea.id}`;
            
            const buttons = [
                { title: 'Bold', action: 'bold', icon: 'B', shortcut: 'Ctrl+B' },
                { title: 'Italic', action: 'italic', icon: 'I', shortcut: 'Ctrl+I' },
                { title: 'Heading', action: 'heading', icon: 'H1', shortcut: 'Ctrl+H' },
                { title: 'Center', action: 'center', icon: '⊗', shortcut: 'Ctrl+E' },
                { title: 'Link', action: 'link', icon: '🔗', shortcut: 'Ctrl+L' },
                { title: 'Image', action: 'image', icon: '🖼️', shortcut: 'Ctrl+Shift+I' },
                { title: 'Code', action: 'code', icon: '</>', shortcut: 'Ctrl+Shift+C' },
                { title: 'Code Block', action: 'codeblock', icon: '⌘', shortcut: 'Ctrl+Shift+B' },
                { title: 'Quote', action: 'quote', icon: '❝', shortcut: 'Ctrl+Q' },
                { title: 'Unordered List', action: 'ul', icon: '•', shortcut: 'Ctrl+U' },
                { title: 'Ordered List', action: 'ol', icon: '1.', shortcut: 'Ctrl+Shift+O' },
                { title: 'Horizontal Rule', action: 'hr', icon: '—', shortcut: 'Ctrl+R' }
            ];

            buttons.forEach(btn => {
                const button = document.createElement('button');
                button.type = 'button';
                button.className = 'markdown-btn';
                button.setAttribute('data-action', btn.action);
                button.setAttribute('data-target', this.textarea.id);
                button.title = `${btn.title} (${btn.shortcut})`;
                button.textContent = btn.icon;
                toolbar.appendChild(button);
            });

            // Add toolbar to container
            this.container.appendChild(toolbar);

            // Safe insertion - replace textarea with container
            try {
                const parent = this.textarea.parentNode;
                parent.replaceChild(this.container, this.textarea);
                this.container.appendChild(this.textarea);
            } catch (error) {
                // Fallback: just append to parent
                this.textarea.parentNode.appendChild(this.container);
                this.container.appendChild(this.textarea);
            }
            
            this.toolbar = toolbar;
        }

        bindEvents() {
            const self = this;
            
            // Button click events - scoped to this toolbar only
            if (this.toolbar) {
                this.toolbar.addEventListener('click', function(e) {
                    if (e.target.classList.contains('markdown-btn')) {
                        e.preventDefault();
                        const action = e.target.getAttribute('data-action');
                        const targetId = e.target.getAttribute('data-target');
                        
                        // Only process if button belongs to this editor
                        if (targetId === self.textarea.id) {
                            self.applyFormat(action);
                        }
                    }
                });
            }

            // Keyboard shortcuts - scoped to this textarea only
            this.textarea.addEventListener('keydown', function(e) {
                // Only apply shortcuts when this textarea has focus
                if (document.activeElement !== self.textarea) {
                    return;
                }
                
                if (e.ctrlKey || e.metaKey) {
                    switch (e.which) {
                        case 66: // Ctrl+B
                            e.preventDefault();
                            self.applyFormat('bold');
                            break;
                        case 73: // Ctrl+I
                            e.preventDefault();
                            self.applyFormat('italic');
                            break;
                        case 72: // Ctrl+H
                            e.preventDefault();
                            self.applyFormat('heading');
                            break;
                        case 69: // Ctrl+E
                            e.preventDefault();
                            self.applyFormat('center');
                            break;
                        case 76: // Ctrl+L
                            e.preventDefault();
                            self.applyFormat('link');
                            break;
                        case 82: // Ctrl+R
                            e.preventDefault();
                            self.applyFormat('hr');
                            break;
                    }
                    
                    if (e.shiftKey) {
                        switch (e.which) {
                            case 67: // Ctrl+Shift+C
                                e.preventDefault();
                                self.applyFormat('code');
                                break;
                            case 73: // Ctrl+Shift+I
                                e.preventDefault();
                                self.applyFormat('image');
                                break;
                            case 66: // Ctrl+Shift+B
                                e.preventDefault();
                                self.applyFormat('codeblock');
                                break;
                            case 81: // Ctrl+Shift+Q
                                e.preventDefault();
                                self.applyFormat('quote');
                                break;
                            case 79: // Ctrl+Shift+O
                                e.preventDefault();
                                self.applyFormat('ol');
                                break;
                        }
                    }
                } else if (e.which === 85) { // Ctrl+U
                    e.preventDefault();
                    self.applyFormat('ul');
                }
            });
        }

        applyFormat(action) {
            const textarea = this.textarea;
            const start = textarea.selectionStart;
            const end = textarea.selectionEnd;
            const selectedText = textarea.value.substring(start, end);
            const beforeText = textarea.value.substring(0, start);
            const afterText = textarea.value.substring(end);

            let newText = '';
            let cursorPos = 0;

            switch (action) {
                case 'bold':
                    newText = `**${selectedText || 'bold text'}**`;
                    cursorPos = start + (selectedText ? newText.length : 12);
                    break;
                    
                case 'italic':
                    newText = `*${selectedText || 'italic text'}*`;
                    cursorPos = start + (selectedText ? newText.length : 14);
                    break;
                    
                case 'heading':
                    newText = `\n# ${selectedText || 'Heading'}\n`;
                    cursorPos = start + newText.length;
                    break;
                    
                case 'center':
                    newText = `<center>${selectedText || 'Centered text'}</center>`;
                    cursorPos = start + newText.length;
                    break;
                    
                case 'link':
                    const linkText = selectedText || 'link text';
                    const url = prompt('Enter URL:');
                    if (url) {
                        newText = `[${linkText}](${url})`;
                        cursorPos = start + newText.length;
                    } else {
                        return;
                    }
                    break;
                    
                case 'image':
                    const imgAlt = selectedText || 'image';
                    const imgUrl = prompt('Enter image URL:');
                    if (imgUrl) {
                        newText = `![${imgAlt}](${imgUrl})`;
                        cursorPos = start + newText.length;
                    } else {
                        return;
                    }
                    break;
                    
                case 'code':
                    newText = `\`${selectedText || 'code'}\``;
                    cursorPos = start + newText.length;
                    break;
                    
                case 'codeblock':
                    newText = `\n\`\`\`\n${selectedText || 'code block'}\n\`\`\`\n`;
                    cursorPos = start + newText.length;
                    break;
                    
                case 'quote':
                    newText = `\n> ${selectedText || 'quote'}\n`;
                    cursorPos = start + newText.length;
                    break;
                    
                case 'ul':
                    const ulText = selectedText ? selectedText.split('\n').map(line => line ? `- ${line}` : line).join('\n') : (selectedText || 'list item');
                    newText = `\n${ulText}\n`;
                    cursorPos = start + newText.length;
                    break;
                    
                case 'ol':
                    const olText = selectedText ? selectedText.split('\n').map((line, i) => line ? `${i + 1}. ${line}` : line).join('\n') : (selectedText || 'list item');
                    newText = `\n${olText}\n`;
                    cursorPos = start + newText.length;
                    break;
                    
                case 'hr':
                    newText = `\n\n---\n\n`;
                    cursorPos = start + newText.length;
                    break;
            }

            textarea.value = beforeText + newText + afterText;
            
            // Set cursor position
            textarea.setSelectionRange(cursorPos, cursorPos);
            textarea.focus();
        }
    }

    // Initialize markdown editors when DOM is ready
    function initializeMarkdownEditors() {
        const contentField = document.getElementById('id_content');
        
        if (contentField) {
            new MarkdownEditor(contentField);
        }
    }

    // Wait for DOM to be ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initializeMarkdownEditors);
    } else {
        initializeMarkdownEditors();
    }

})();