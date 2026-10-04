-- Seed Initial News Sources for Crab News
-- Indonesian News Portals (Antara, CNN Indonesia, Kompas, Detik, Tempo)

INSERT INTO public.sources (id, name, slug, domain, website_url, rss_url, crawler_type, is_active)
VALUES
    (
        'a0000000-0000-0000-0000-000000000001',
        'Antara News',
        'antara',
        'antaranews.com',
        'https://www.antaranews.com',
        'https://www.antaranews.com/rss/terkini.xml',
        'rss',
        true
    ),
    (
        'a0000000-0000-0000-0000-000000000002',
        'CNN Indonesia',
        'cnn-indonesia',
        'cnnindonesia.com',
        'https://www.cnnindonesia.com',
        'https://www.cnnindonesia.com/nasional/rss',
        'rss',
        true
    ),
    (
        'a0000000-0000-0000-0000-000000000003',
        'Kompas',
        'kompas',
        'kompas.com',
        'https://www.kompas.com',
        'https://news.kompas.com/feed',
        'rss',
        true
    ),
    (
        'a0000000-0000-0000-0000-000000000004',
        'Detik News',
        'detik',
        'detik.com',
        'https://news.detik.com',
        'https://rss.detik.com/index.php/detikcom',
        'rss',
        true
    ),
    (
        'a0000000-0000-0000-0000-000000000005',
        'Tempo',
        'tempo',
        'tempo.co',
        'https://www.tempo.co',
        'https://rss.tempo.co/nasional',
        'rss',
        true
    )
ON CONFLICT (slug) DO UPDATE SET
    name = EXCLUDED.name,
    domain = EXCLUDED.domain,
    website_url = EXCLUDED.website_url,
    rss_url = EXCLUDED.rss_url,
    crawler_type = EXCLUDED.crawler_type,
    is_active = EXCLUDED.is_active,
    updated_at = NOW();
