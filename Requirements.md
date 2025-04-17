# YouTube Tag Generator Web Application

## Project Overview
A web application built with React Native (Expo) that helps content creators generate optimized tags and keywords for their YouTube videos.

## Core Features

### 1. Tag Generator
- Input fields for video title and description
- Smart tag generation based on content analysis
- Tag character count and limit indicator
- Copy-to-clipboard functionality
- Tag preview in YouTube format
- Tag editing and customization
- Popular category-based tag suggestions

### 2. Keyword Research
- Topic-based keyword suggestions
- Common YouTube keyword patterns
- Keyword combination generator
- Category-specific keyword templates
- Export keywords in YouTube-friendly format

### 3. Tag Management
- Save tags locally
- Organize tags by categories
- Quick-access to frequently used tags
- Tag format validation
- Character count optimization

## Technical Requirements

### Frontend
- React Native with Expo
- Clean folder structure
- Responsive design for all screen sizes
- Modern UI/UX with intuitive navigation

### Screens (in /app folder)
1. Home Screen (Tag Generator)
2. Saved Tags Screen
3. Category Templates Screen
4. Help & Guidelines Screen

### Components
- Tag Input Component
- Tag Display Component
- Category Selector
- Copy Button Component
- Tag Preview Component
- Character Counter Component

## User Experience
- Simple and intuitive interface
- Quick tag generation
- Easy tag editing and management
- Clear feedback on tag limits
- Helpful tooltips and guides
- Offline functionality

## Project Structure
```bash
/app
  /_layout.js
  /index.js
  /saved-tags.js
  /templates.js
  /help.js
  /components
    /TagInput.js
    /TagDisplay.js
    /CategorySelector.js
    /TagPreview.js
  /utils
    /tagGenerator.js
    /categoryData.js
    /validation.js
  /hooks
    /useTagGenerator.js
    /useLocalStorage.js
```

## Performance Requirements
- Instant tag generation
- Smooth UI interactions
- Efficient local storage management
- Responsive across all devices

## Future Enhancements
- Advanced tag analysis
- Custom tag templates
- Tag effectiveness tips
- Batch tag generation
- Export/Import functionality

Would you like me to start implementing this structure, beginning with any particular component or screen?
