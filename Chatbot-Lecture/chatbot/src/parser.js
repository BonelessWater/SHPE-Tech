import React from 'react';

export function parseContent(content) {
  const lines = content.split('\n'); // Split content by newlines
  let parsedContent = [];
  let isCodeBlock = false; // Track if we're inside a code block
  let codeLines = []; // To store lines inside a code block

  lines.forEach((line, index) => {
    if (line.startsWith('### ')) {
      // Main heading
      parsedContent.push(<h3 key={index}>{line.slice(4)}</h3>);
    } else if (line.startsWith('#### ')) {
      // Subheading
      parsedContent.push(<h4 key={index}>{line.slice(5)}</h4>);
    } else if (line.startsWith('```')) {
      // Toggle code block state
      if (isCodeBlock) {
        // Closing code block
        parsedContent.push(
          <pre key={index}>
            <code>{codeLines.join('\n')}</code>
          </pre>
        );
        codeLines = []; // Clear code lines for the next block
      }
      isCodeBlock = !isCodeBlock;
    } else if (isCodeBlock) {
      // Collect lines inside a code block
      codeLines.push(line);
    } else if (line.startsWith('- ')) {
      // Bullet list item
      parsedContent.push(<li key={index}>{line.slice(2)}</li>);
    } else if (line.trim() === '') {
      // Add a break line for empty lines
      parsedContent.push(<br key={index} />);
    } else {
      // Regular paragraph
      parsedContent.push(<p key={index}>{line}</p>);
    }
  });

  return parsedContent;
}
