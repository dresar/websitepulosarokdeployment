# Public Website Templates

This directory contains the public-facing templates for the Desa Pulosarok website.

## Templates Created

### 1. `base.html` - Base Template
- **Purpose**: Main layout template for all public pages
- **Features**:
  - Responsive navigation with mobile menu
  - Dynamic website settings integration
  - Dark/light theme support
  - SEO-optimized meta tags
  - Social media integration
  - Footer with contact information
  - Smooth scrolling and animations

### 2. `home.html` - Home Page Template
- **Purpose**: Main landing page for the website
- **Features**:
  - Hero section with dynamic content
  - Statistics dashboard (population, families, etc.)
  - Latest news section
  - Featured businesses (UMKM)
  - Tourism destinations
  - Village officials
  - Quick services access
  - Contact information
  - Responsive design for all devices

## Template Features

### Responsive Design
- Mobile-first approach
- Breakpoints: 640px, 768px, 1024px, 1280px
- Flexible grid layouts
- Touch-friendly navigation

### Dynamic Content
- Website settings integration
- Real-time data from database
- Conditional content display
- Error handling for missing data

### Performance Optimizations
- Lazy loading for images
- CSS and JS minification ready
- Optimized animations
- Efficient DOM manipulation

### Accessibility
- Semantic HTML structure
- ARIA labels and roles
- Keyboard navigation support
- Screen reader friendly

## Usage

### Extending the Base Template
```html
{% extends 'public/base.html' %}
{% load static %}

{% block title %}Your Page Title{% endblock %}

{% block extra_css %}
<style>
    /* Your custom CSS */
</style>
{% endblock %}

{% block content %}
<!-- Your page content -->
{% endblock %}

{% block extra_js %}
<script>
    // Your custom JavaScript
</script>
{% endblock %}
```

### Available Blocks
- `title`: Page title
- `meta_description`: Meta description
- `meta_keywords`: Meta keywords
- `og_title`: Open Graph title
- `og_description`: Open Graph description
- `og_image`: Open Graph image
- `twitter_title`: Twitter card title
- `twitter_description`: Twitter card description
- `twitter_image`: Twitter card image
- `extra_css`: Additional CSS
- `content`: Main content area
- `extra_js`: Additional JavaScript

## Data Context

The templates expect the following context variables:

### Base Template
- `website_settings`: WebsiteSettings object
- `request`: Django request object

### Home Template
- `page_title`: Page title (default: "Beranda")
- `page_subtitle`: Page subtitle
- `hero_image`: Hero section image
- `latest_news`: List of latest news articles
- `announcements`: List of active announcements
- `featured_businesses`: List of featured businesses
- `tourism_locations`: List of tourism locations
- `village_officials`: List of village officials
- `total_population`: Total population count
- `total_families`: Total families count
- `male_population`: Male population count
- `female_population`: Female population count

## Styling

### CSS Variables
The templates use CSS custom properties for theming:
- `--primary-color`: Primary brand color
- `--secondary-color`: Secondary brand color
- `--bg-primary`: Primary background
- `--bg-secondary`: Secondary background
- `--text-primary`: Primary text color
- `--text-secondary`: Secondary text color
- `--border-color`: Border color

### Color Scheme
- Primary: Blue (#3B82F6)
- Secondary: Green (#10B981)
- Success: Green variants
- Warning: Yellow variants
- Error: Red variants
- Info: Blue variants

## JavaScript Features

### Interactive Elements
- Mobile menu toggle
- Smooth scrolling
- Counter animations
- Scroll-triggered animations
- Loading states
- Theme switching (if implemented)

### Performance
- Intersection Observer for animations
- Debounced scroll events
- Efficient DOM queries
- Minimal JavaScript footprint

## Browser Support

- Chrome 60+
- Firefox 60+
- Safari 12+
- Edge 79+
- Mobile browsers (iOS Safari, Chrome Mobile)

## Dependencies

### External CDN
- Tailwind CSS 2.2.19
- Font Awesome 6.0.0
- Google Fonts (Inter)
- Alpine.js 3.x

### Django Requirements
- Django 4.0+
- Python 3.8+

## Customization

### Adding New Sections
1. Create new template blocks
2. Add corresponding CSS
3. Update JavaScript if needed
4. Test responsiveness

### Modifying Styles
1. Override CSS variables
2. Add custom CSS in `extra_css` block
3. Use Tailwind utility classes
4. Maintain responsive design

### Adding New Features
1. Update base template if global
2. Create new templates for specific pages
3. Follow existing patterns
4. Test across devices

## Troubleshooting

### Common Issues
1. **Static files not loading**: Run `python manage.py collectstatic`
2. **Template not found**: Check template path and extends
3. **Context variables missing**: Verify view context
4. **Responsive issues**: Check breakpoints and CSS
5. **JavaScript errors**: Check console and dependencies

### Debug Mode
Enable Django debug mode to see detailed error messages:
```python
DEBUG = True
```

## Future Enhancements

### Planned Features
- Progressive Web App (PWA) support
- Advanced animations
- Real-time updates
- Offline functionality
- Advanced accessibility features

### Performance Improvements
- Image optimization
- Code splitting
- Service worker integration
- Advanced caching strategies
