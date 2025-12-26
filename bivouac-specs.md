# 🏔️ Bivouac.tv — Technical Specifications

> **The basecamp for adventure, nature & extreme sports documentaries**

---

## 📋 Executive Summary

**Bivouac.tv** is a community-driven discovery platform for adventure/nature/extreme sports documentaries. It aggregates content scattered across Netflix, Arte, YouTube, Vimeo, Red Bull TV, and others — allowing users to find, rate, and share their discoveries.

**Positioning:** "Letterboxd meets JustWatch" for outdoor docs.

---

## 🎯 Core Features

### Phase 1 — MVP (v1.0)

| Feature | Description | Priority |
|---------|-------------|----------|
| **Doc Database** | Browse all documentaries with metadata | 🔴 Critical |
| **Search & Filters** | By sport, region, platform, free/paid | 🔴 Critical |
| **"Where to Watch"** | Links to streaming platforms | 🔴 Critical |
| **User Accounts** | Register, login, profile | 🔴 Critical |
| **Watchlist** | Save docs to watch later | 🟡 High |
| **Ratings & Reviews** | Rate (1-5) + short review | 🟡 High |
| **Doc Submission** | Users can suggest new docs | 🟡 High |

### Phase 2 — Community (v1.5)

| Feature | Description |
|---------|-------------|
| **Curated Lists** | "Best climbing docs", "Free on YouTube", etc. |
| **User Lists** | Users create & share their own lists |
| **Follow Users** | Follow other adventure doc lovers |
| **Activity Feed** | See what people are watching/rating |
| **Comments** | Discuss on doc pages |
| **Community Tagging** | Users suggest sports/themes/regions, mods approve |

### Phase 3 — Growth (v2.0)

| Feature | Description |
|---------|-------------|
| **Notifications** | "New climbing doc on Netflix!" |
| **Recommendations** | "Based on your taste..." |
| **Mobile App** | React Native or PWA |
| **API** | Public API for partners |

---

## 🗃️ Data Models

### Documentary
```python
class Documentary(models.Model):
    title = models.CharField(max_length=255)
    original_title = models.CharField(max_length=255, blank=True)
    slug = models.SlugField(unique=True)
    
    year = models.PositiveIntegerField()
    duration_minutes = models.PositiveIntegerField()
    
    synopsis = models.TextField()
    poster = models.ImageField(upload_to='posters/')
    backdrop = models.ImageField(upload_to='backdrops/', blank=True)
    trailer_url = models.URLField(blank=True)
    
    directors = models.ManyToManyField('Person', related_name='directed')
    
    sports = models.ManyToManyField('Sport')       # climbing, surf, ski...
    themes = models.ManyToManyField('Theme')       # wildlife, expedition, portrait...
    regions = models.ManyToManyField('Region')     # Alps, Patagonia, Nepal...
    
    imdb_id = models.CharField(max_length=20, blank=True)
    imdb_rating = models.DecimalField(max_digits=3, decimal_places=1, null=True)
    
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

### Platform & Availability
```python
class Platform(models.Model):
    name = models.CharField(max_length=100)  # Netflix, Arte, YouTube...
    slug = models.SlugField(unique=True)
    logo = models.ImageField(upload_to='platforms/')
    website = models.URLField()
    is_free = models.BooleanField(default=False)

class Availability(models.Model):
    documentary = models.ForeignKey(Documentary, on_delete=models.CASCADE)
    platform = models.ForeignKey(Platform, on_delete=models.CASCADE)
    url = models.URLField()
    is_free = models.BooleanField(default=False)
    available_from = models.DateField(null=True)
    available_until = models.DateField(null=True)  # Netflix rotations
    country_codes = models.JSONField(default=list)  # ['FR', 'BE', 'CH']
    last_checked = models.DateTimeField(auto_now=True)
```

### User Interactions
```python
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/', blank=True)
    bio = models.TextField(max_length=500, blank=True)
    favorite_sports = models.ManyToManyField('Sport', blank=True)

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    documentary = models.ForeignKey(Documentary, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    content = models.TextField(max_length=2000, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'documentary']

class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    documentary = models.ForeignKey(Documentary, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'documentary']
```

### Submissions
```python
class Submission(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    submitted_by = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    year = models.PositiveIntegerField()
    url = models.URLField(help_text="Link to trailer or platform")
    notes = models.TextField(blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    reviewed_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name='reviewed_submissions')
    created_at = models.DateTimeField(auto_now_add=True)
```

---

## 🛠️ Technical Stack

### Backend
| Component | Technology |
|-----------|------------|
| Framework | Django 5.x |
| API | Django REST Framework |
| Auth | dj-rest-auth + django-allauth |
| Database | PostgreSQL 15 |
| Cache | Redis |
| Task Queue | Celery (for notifications, availability checks) |
| Search | PostgreSQL Full-Text → Meilisearch (later) |
| Storage | AWS S3 / Cloudflare R2 |

### Frontend
| Component | Technology |
|-----------|------------|
| Framework | Vue.js 3 (Composition API) |
| Build | Vite |
| Styling | Tailwind CSS |
| State | Pinia |
| Router | Vue Router |
| HTTP | Axios |
| Icons | Lucide Icons |

### Infrastructure
| Component | Technology |
|-----------|------------|
| Backend Hosting | Railway / Render |
| Frontend Hosting | Vercel / Netlify |
| Database | Railway PostgreSQL / Supabase |
| CDN | Cloudflare |
| Domain | bivouac.tv |

---

## 📁 Project Structure

### Backend (Django)
```
bivouac-api/
├── config/
│   ├── settings/
│   │   ├── base.py
│   │   ├── development.py
│   │   └── production.py
│   ├── urls.py
│   └── wsgi.py
├── apps/
│   ├── documentaries/
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── filters.py
│   │   └── urls.py
│   ├── users/
│   ├── reviews/
│   ├── lists/
│   └── submissions/
├── manage.py
└── requirements/
    ├── base.txt
    ├── development.txt
    └── production.txt
```

### Frontend (Vue.js)
```
bivouac-web/
├── src/
│   ├── assets/
│   ├── components/
│   │   ├── common/
│   │   ├── docs/
│   │   └── layout/
│   ├── composables/
│   ├── pages/
│   │   ├── Home.vue
│   │   ├── Browse.vue
│   │   ├── DocDetail.vue
│   │   ├── Profile.vue
│   │   └── auth/
│   ├── router/
│   ├── stores/
│   ├── services/
│   │   └── api.js
│   ├── App.vue
│   └── main.js
├── index.html
├── vite.config.js
├── tailwind.config.js
└── package.json
```

---

## 📊 Current Data Status (Dec 2024)

| Metric | Count | Notes |
|--------|-------|-------|
| **Total Documentaries** | 120 | FIFAV winners 2004-2025 |
| **Published (visible)** | 76 | Have TMDB metadata |
| **With Posters** | 67 | Downloaded from TMDB |
| **With Backdrops** | 42 | Fallback to poster implemented |
| **Directors** | 137 | Parsed from festival data |
| **Sports** | 20 | Seeded taxonomy |
| **Themes** | 18 | Seeded taxonomy |
| **Regions** | 39 | Seeded taxonomy |
| **Platforms** | 15 | Seeded (Netflix, Arte, YouTube, etc.) |

### Data Commands
```bash
# Import FIFAV festival winners
uv run python manage.py import_fifav

# Seed sports, themes, regions, platforms
uv run python manage.py seed_taxonomies

# Enrich with TMDB (posters, synopsis, trailers)
uv run python manage.py enrich_tmdb

# Download poster images
uv run python manage.py download_posters

# Auto-tag with sports/themes from TMDB keywords
uv run python manage.py autotag_tmdb
```

### Tagging Strategy

| Method | Status | Notes |
|--------|--------|-------|
| **Manual tagging** | ✅ Done | Initial 76 docs tagged manually |
| **TMDB keywords** | ✅ Done | `autotag_tmdb` command (low match rate for niche docs) |
| **AI-powered tagging** | 🔜 Planned | Claude API command to analyze synopsis/title |
| **Community tagging** | 🔜 Phase 2 | Users suggest tags, moderators approve |

**Future: AI Auto-Tagging Command**
```bash
# Will use Claude API to intelligently tag from synopsis
uv run python manage.py autotag_ai --api-key $ANTHROPIC_API_KEY
```

---

## 🌱 Database Growth Strategy

### Phase 1: Manual Seeding (Month 1-2)
- **You** add 100-200 docs you personally know
- Focus on quality over quantity
- Cover all main categories (climbing, surf, ski, wildlife, travel)

### Phase 2: Community Submissions (Month 2+)
- Users submit docs via form
- You moderate and approve
- Gamification: "Top contributors" badge

### Phase 3: Data Sources (Month 3+)
| Source | How |
|--------|-----|
| **TMDB API** | Filter documentaries by keywords |
| **IMDB Datasets** | Public datasets, filter by genre |
| **YouTube API** | Search channels (Red Bull, Patagonia, etc.) |
| **Web Scraping** | Film festival catalogs (Banff, Kendal, etc.) |
| **Partnerships** | Contact Adventure+, Redbull TV for data sharing |

### Phase 4: Availability Tracking (Month 6+)
- Celery jobs to check platform availability weekly
- JustWatch has no public API, but TMDB has "watch providers"
- Manual community updates for niche platforms (Arte, Vimeo)

---

## 💰 Monetization Strategy

### Tier 1: Passive Income (Day 1)

| Method | How | Potential |
|--------|-----|-----------|
| **Affiliate Links** | Amazon, iTunes links for docs to buy/rent | €50-200/mo |
| **Platform Referrals** | Some platforms have affiliate programs | Variable |

### Tier 2: Advertising (1000+ daily users)

| Method | How | Potential |
|--------|-----|-----------|
| **Tasteful Ads** | Outdoor brands (Patagonia, Salomon, etc.) | €200-500/mo |
| **Sponsored Docs** | "Featured Documentary" slot | €100-300/placement |
| **Newsletter Sponsors** | Weekly digest with sponsor | €50-150/issue |

### Tier 3: Premium Features (5000+ users)

| Feature | Price | Value |
|---------|-------|-------|
| **Bivouac Pro** | €3/mo or €25/yr | Ad-free, early access, exclusive lists |
| **Notifications** | Pro only | "Alert me when X is free" |
| **Advanced Filters** | Pro only | Filter by duration, rating, language |
| **API Access** | €10/mo | For developers/bloggers |

### Tier 4: Partnerships (Established)

| Partner Type | Revenue |
|--------------|---------|
| **Streaming Platforms** | Paid placement, data deals |
| **Film Festivals** | Banff, Kendal — official catalog partner |
| **Outdoor Brands** | Sponsored lists, content partnerships |
| **Travel Agencies** | "Docs that inspired this trip" |

### Revenue Projections (Realistic)

| Timeline | Monthly Users | Revenue |
|----------|---------------|---------|
| Month 6 | 1,000 | €0-50 (affiliate) |
| Year 1 | 5,000 | €100-300 |
| Year 2 | 20,000 | €500-1,500 |
| Year 3 | 50,000+ | €2,000-5,000 |

---

## 🚀 Development Roadmap

### Sprint 1: Foundation ✅ DONE
- [x] Django project setup with uv
- [x] Core models (Documentary, Platform, Availability, Sport, Theme, Region, Person)
- [x] Django Admin customization
- [x] Vue.js 3 project setup + Tailwind + TypeScript
- [x] Basic API endpoints (list, detail, filter)
- [x] FIFAV data import (120 documentaries from 2004-2025)
- [x] TMDB enrichment pipeline (posters, synopses, trailers)
- [x] Taxonomy seeding (20 sports, 18 themes, 39 regions, 15 platforms)

### Sprint 2: Core Features ✅ DONE
- [x] Homepage with featured/top-rated/recent sections
- [x] Browse page with filters (sport, platform, region, free, sorting)
- [x] Documentary detail page
- [x] ~~**FIX: Browse page shows no results**~~ Fixed: `is_free` filter was incorrectly sent as `false`
- [x] ~~**FIX: Backdrop fallback to poster**~~ Fixed: Blurred poster as ambient background (Netflix-style)
- [x] "Where to watch" component (shows placeholder when no availability data)
- [x] Search functionality (full-text search)
- [x] **Infinite scroll** on Browse page (lazy loading with Intersection Observer)

### Sprint 3: Users ✅ DONE
- [x] User registration/login (email)
- [x] User profile page (read-only)
- [x] Watchlist functionality (add/remove)
- [x] **Ratings & Reviews UI** - Star rating + review form on doc detail page
- [x] **Profile editing** - Edit username and bio

### Sprint 4: Community 🔜 NEXT
- [x] **Reviews UI** - Display reviews on doc page + submission form
- [x] Doc submission form (basic)
- [ ] Admin moderation queue improvements
- [ ] Basic SEO (meta tags, sitemap)

### Sprint 5: Data & Polish 🔜 UPCOMING
- [ ] **Better tagging** - Auto-detect sports/themes from TMDB keywords
- [X] **Homepage hero** - JustWatch-style backdrop with featured doc
- [ ] Mobile responsive polish
- [ ] Performance optimization
- [ ] Error handling & loading states
- [ ] Analytics setup (Plausible/Umami)

---

## 🐛 Known Issues & Next Steps

### Priority 1: Critical Fixes ✅ RESOLVED
| Issue | Description | Status |
|-------|-------------|--------|
| ~~Browse shows nothing~~ | Fixed: `is_free=false` filter bug | ✅ Fixed |
| ~~No backdrop fallback~~ | Fixed: Falls back to poster image | ✅ Fixed |

### Priority 2: Missing Features
| Feature | Description | Status |
|---------|-------------|--------|
| ~~Reviews UI~~ | Show reviews + rating form on doc detail | ✅ Done |
| ~~Ratings UI~~ | Star rating component on doc detail | ✅ Done |
| ~~Auto-tagging~~ | Parse TMDB keywords → sports/themes | ✅ Done |
| Hero section | Full-bleed backdrop like JustWatch | ✅ Done |
| Availability data | Where to watch links (need data) | 🟡 Need data |

### Priority 3: Enhancements
| Feature | Description | Status |
|---------|-------------|--------|
| ~~Year/Duration filters~~ | Exposed in Browse UI | ✅ Done |
| ~~Theme filter~~ | Exposed in Browse UI | ✅ Done |
| ~~Pagination~~ | Infinite scroll implemented | ✅ Done |
| ~~Profile editing~~ | Edit username and bio | ✅ Done |

whats next:
- proper scrapping workflow
  - i find the list of documentaries title, we need to:
  - check tmdb to find basic metadata
  - if not found, or if found but sometimes we have no posters, no synopsis (very important) or no trailer, so we need to scrap that
  - use AI to generate tags / location
  - find a way to scrap "Where to watch links"
- user profile enhancements:
  - add funny pre loaded avatars, based on our themes
  - or user can add a profile picture
  - user can add new documentaries
  - user can add new "Where to watch links"
  - create and give badges to users based on their commitment
  - add a most proficient users section in home page
  - show user badges next to their profile (in reviews, etc)
- users public watchlist:
  - add a full list creation/visualization made by users for public use
- we have 'add to watchlist', we need know 'watched' | ✅ Done |
- add a 'favorite' list + icon | ✅ Done |
- when user commits some changes, add a system of admin queue validation (me) | ✅ Done |
- enhance homepage, like justwatch, with "sliders" of movies based on popular themes, like 'popular', 'survival', 'mountain', etc...  | ✅ Done |
- put all the filters on the footer
- make the website fr / eng trad | ✅ Done |
- from detailed doc view, make the directors name clickable, and filter docs
- add public API
- add platform icons in "where to watch" links in doc detail

---

## 📈 Launch Strategy

### Pre-Launch
1. Seed database with 150+ docs
2. Create social accounts (Twitter, Instagram, Letterboxd)
3. Build email waitlist landing page

### Launch Week
1. Post on Reddit: r/Documentaries, r/climbing, r/surfing, r/alpinism
2. Product Hunt launch
3. Hacker News "Show HN"
4. Contact outdoor bloggers for coverage

### Post-Launch
1. Weekly newsletter with new additions
2. Engage community on social
3. Respond to feature requests
4. Iterate based on feedback

---

## 📝 Success Metrics

| Metric | Month 1 | Month 6 | Year 1 |
|--------|---------|---------|--------|
| Docs in DB | 200 | 500 | 1,000+ |
| Monthly Users | 500 | 3,000 | 10,000 |
| Registered Users | 50 | 500 | 2,000 |
| Reviews | 20 | 200 | 1,000 |
| Newsletter Subs | 100 | 500 | 2,000 |

---

*Let's build this.* 🏔️
