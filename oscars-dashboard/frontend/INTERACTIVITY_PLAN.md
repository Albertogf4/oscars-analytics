# Interactivity Enhancement Plan for Oscar Markets Dashboard

## Current State Analysis

**Tech Stack:**
- React 19 + TypeScript
- Vite 7.3
- Tailwind CSS v4
- Framer Motion (already installed)

**Existing Interactivity:**
- `.hover-lift` class: simple -2px vertical lift on hover
- Framer Motion fade-in and stagger animations on page load
- Animated bar chart width expansion
- Loading spinner animation

**Components to Enhance:**
1. MovieCard.tsx
2. CategoryChart.tsx
3. ComparisonTable.tsx
4. Layout.tsx
5. Dashboard.tsx (All Markets tables)
6. index.css (global styles)

---

## Implementation Plan

### 1. Enhanced Global Styles (index.css)

**New CSS Classes:**

```css
/* Enhanced card hover with shadow depth + subtle glow */
.card-interactive {
  transition: transform 0.3s ease, box-shadow 0.3s ease, border-color 0.3s ease;
}
.card-interactive:hover {
  transform: translateY(-4px);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4);
  border-color: var(--color-border-light);
}

/* Glowing border effect for frontrunner cards */
.glow-gold {
  transition: box-shadow 0.3s ease;
}
.glow-gold:hover {
  box-shadow: 0 0 20px rgba(212, 175, 55, 0.3);
}

/* Interactive price pulse animation */
@keyframes pricePulse { ... }

/* Table row hover */
.table-row-interactive:hover {
  background-color: rgba(38, 38, 38, 0.5);
}

/* Button/Badge hover effects */
.badge-interactive:hover {
  transform: scale(1.05);
  filter: brightness(1.1);
}

/* Smooth scroll for entire page */
html { scroll-behavior: smooth; }
```

---

### 2. MovieCard.tsx Enhancements

| Element | Current | Enhanced |
|---------|---------|----------|
| Card container | hover-lift (-2px) | Scale 1.02, deeper shadow, border glow |
| Rank badge | Static | Hover: background color shift |
| Best Picture price | Static color | Subtle pulse animation when >50% |
| Metrics grid | Static | Individual cell hover highlight |
| Category tags | Static | Hover: scale + color pop |
| "+X more" text | Static | Hover: expand to show all |

**Implementation:**
- Add `whileHover` prop to motion.div with scale and shadow
- Add `whileTap` for click feedback
- Add hover states to category tags with Tailwind
- Animate price display with CSS keyframes when high odds

---

### 3. CategoryChart.tsx Enhancements

| Element | Current | Enhanced |
|---------|---------|----------|
| Chart bars | Animated width on load | Hover: brightness + tooltip |
| Bar container | Static | Cursor pointer, subtle lift |
| Movie labels | Static | Hover: color shift |
| Legend items | Static | Hover: highlight corresponding bars |

**Implementation:**
- Add `whileHover={{ scale: 1.02, filter: 'brightness(1.1)' }}` to bars
- Add tooltip showing exact percentage + volume on hover
- Cursor pointer on interactive elements
- Legend hover state that highlights related data

---

### 4. ComparisonTable.tsx Enhancements

| Element | Current | Enhanced |
|---------|---------|----------|
| Table rows | Animated slide-in | Hover: background highlight |
| Table cells | Static | Hover: cell emphasis |
| Price values | Static | Hover: show change indicator |
| Header columns | Static | Click to sort (visual feedback) |

**Implementation:**
- Add `hover:bg-bg-secondary/50` to table rows
- Add transition for background color
- Visual indicator on cell hover
- Sort functionality with animated reordering

---

### 5. Layout.tsx Enhancements

| Element | Current | Enhanced |
|---------|---------|----------|
| Header title | Static | Hover: subtle color shift/underline |
| "Last Updated" | Static | Pulse animation when data refreshes |
| Footer | Static | Link hover states |

**Implementation:**
- Add text hover effects to header
- Subtle gradient animation on title
- Footer link hover underline animation

---

### 6. Dashboard.tsx Enhancements

| Element | Current | Enhanced |
|---------|---------|----------|
| Section headers | Static | Hover: subtle lift |
| All Markets table rows | Static | Hover: highlight row |
| "Showing X of Y" text | Static | Clickable to expand all |
| Market titles | Static truncate | Hover: expand/tooltip |

**Implementation:**
- Add row hover states to "All Markets" tables
- Expand/collapse button with animation
- Truncated text shows full on hover

---

## Files to Modify

1. **index.css** - Add new utility classes and animations
2. **MovieCard.tsx** - Enhanced hover animations and interactions
3. **CategoryChart.tsx** - Bar hover effects and tooltips
4. **ComparisonTable.tsx** - Row/cell hover states
5. **Layout.tsx** - Header/footer interactions
6. **Dashboard.tsx** - Table row hovers, expand functionality

---

## Priority Order

1. **High Impact, Low Effort:**
   - Card hover enhancements (MovieCard)
   - Table row hover states (ComparisonTable, Dashboard)
   - Global CSS utility classes

2. **Medium Impact:**
   - Category chart bar interactions
   - Category tag hover effects
   - Legend interactivity

3. **Polish:**
   - Header/footer animations
   - Price pulse animations
   - Expand/collapse for long lists

---

## Summary

This plan adds rich interactivity while maintaining the clean, Harvey-inspired dark aesthetic. All enhancements use existing dependencies (Framer Motion + Tailwind) and follow the established patterns in the codebase.

**Total files to modify:** 6
**New dependencies:** None