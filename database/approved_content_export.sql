-- CannTech Approved Content Export
-- Generated: 2025-09-06T11:25:57.049189
-- Total items: 19

-- Ensure content_feeds table exists with proper schema
CREATE TABLE IF NOT EXISTS content_feeds (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    content TEXT,
    source TEXT NOT NULL,
    category TEXT,
    url TEXT,
    published_date TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT 1,
    compliance_status TEXT DEFAULT 'pending',
    social_platform TEXT,
    engagement_metrics JSON,
    content_hash VARCHAR(255) UNIQUE,
    approval_timestamp DATETIME,
    priority INTEGER DEFAULT 3
);

-- Clear existing approved content to avoid duplicates
DELETE FROM content_feeds WHERE compliance_status = 'approved';

-- Insert approved content items
INSERT INTO content_feeds (
    title, content, source, category, url, published_date, created_at,
    is_active, compliance_status, engagement_metrics, content_hash,
    approval_timestamp, priority
) VALUES (
    'Canadian Cannabis Market Intelligence: 20,000+ Licensed Retailers Drive $9.2 Billion GDP Impact',
    'Comprehensive analysis showing how Canada''s 20,000+ licensed cannabis retailers create economic stability through regulatory clarity and compliance automation, outpacing US competitors.',
    'CannTech Intelligence',
    'Analysis',
    '/market-analysis.html',
    '2025-09-01 12:00:00',
    '2025-08-28 20:59:54',
    1,
    'approved',
    '{"business_relevance_score": 5.0, "featured": true}',
    '7af932d65d7e32a9103870d9c179599f',
    '2025-09-05 01:58:36',
    1
);
INSERT INTO content_feeds (
    title, content, source, category, url, published_date, created_at,
    is_active, compliance_status, engagement_metrics, content_hash,
    approval_timestamp, priority
) VALUES (
    'Bubble Up - Tribal',
    'Since I enjoy the Cuban Linx, I decided to try another offering from Tribal.  So I picked up another can of Cuban Linx and got 3.5 g can of Bubble Up as well for $22.50 each at Canna Cabana in Winnipeg.  The THC is listed  at 29.6% and terpenes at 2.6%.

Opening the can, I found mostly little nuglets inside.  The trichome coverage is pretty good and the buds are well trimmed.  The buds are a bit o',
    'r/CanadianCannabisLPs',
    'Community',
    'https://reddit.com/r/CanadianCannabisLPs/comments/1n5r5rm/bubble_up_tribal/',
    '2025-09-01 09:05:45',
    '2025-09-01 17:40:01',
    1,
    'approved',
    '{"business_relevance_score": 5.5}',
    'c64f7e064f0dd3b431ddb1116a3ddec0',
    '2025-09-05 01:57:24',
    3
);
INSERT INTO content_feeds (
    title, content, source, category, url, published_date, created_at,
    is_active, compliance_status, engagement_metrics, content_hash,
    approval_timestamp, priority
) VALUES (
    'GrowerIQ International Expansion Signals Canadian Cannabis Tech Leadership',
    'Thailand expansion demonstrates how Canadian cannabis technology companies leverage domestic regulatory expertise for international growth opportunities.',
    'CannTech Intelligence',
    'Company',
    '/international-expansion.html',
    '2025-09-01 12:00:00',
    '2025-08-28 20:59:54',
    1,
    'approved',
    '{"business_relevance_score": 5.0, "featured": true}',
    '10b931cd6fc9aaf8c5d7391634dbbd3f',
    '2025-09-05 01:56:05',
    3
);
INSERT INTO content_feeds (
    title, content, source, category, url, published_date, created_at,
    is_active, compliance_status, engagement_metrics, content_hash,
    approval_timestamp, priority
) VALUES (
    'Gov. Meyer vetoes bill to loosen marijuana zoning regulations in Delaware',
    'Gov. Matt Meyer vetoed a bill Thursday that would have loosened regulations around where marijuana businesses can locate in Delaware, likely further delaying the growth of the weeks-old industry.',
    'Winnipeg Free Press',
    'Regulatory',
    'https://www.winnipegfreepress.com/business/2025/08/29/gov-meyer-vetoes-bill-to-loosen-marijuana-zoning-regulations-in-delaware',
    '2025-08-29 17:49:00',
    '2025-09-05 01:14:08',
    1,
    'approved',
    '{"business_relevance_score": 5.8}',
    '1d9e76ac437dd428485f1556dad76c18',
    '2025-09-05 01:56:05',
    3
);
INSERT INTO content_feeds (
    title, content, source, category, url, published_date, created_at,
    is_active, compliance_status, engagement_metrics, content_hash,
    approval_timestamp, priority
) VALUES (
    'Cannabis Act Compliance Automation: CertiCraft Enables One-Minute Audits',
    'Smart scales, RFID integration, and automated tracking systems deliver 30-40% reduction in human error for Canadian cannabis operations.',
    'CannTech Intelligence',
    'Regulatory',
    '/compliance-analysis.html',
    '2025-09-01 12:00:00',
    '2025-08-28 20:59:54',
    1,
    'approved',
    '{"business_relevance_score": 5.0, "featured": true}',
    '991772c16d0e3fc16d562154a5636e65',
    '2025-09-05 01:55:13',
    3
);
INSERT INTO content_feeds (
    title, content, source, category, url, published_date, created_at,
    is_active, compliance_status, engagement_metrics, content_hash,
    approval_timestamp, priority
) VALUES (
    'Organigram Global Releases Landmark Report: Legal Cannabis Added $16B to Canada''s GDP in 2024',
    'Organigram Global Inc. (NASDAQ: OGI) (TSX: OGI), Canada''s largest cannabis company by market share, today released "High Impact, Green Growth: The Economic Footprint of Canada''s Cannabis Industry," a national report done in partnership with the Business Data Lab at the Canadian Chamber of Commerce.',
    'Yahoo Finance',
    'Industry Commentary',
    'https://finance.yahoo.com/news/organigram-global-releases-landmark-report-100000672.html',
    '2025-09-02 10:10:00',
    '2025-09-05 01:14:08',
    1,
    'approved',
    '{"business_relevance_score": 6.5}',
    'b199c9a10816b7b6f94bf02caa297839',
    '2025-09-05 01:55:13',
    3
);
INSERT INTO content_feeds (
    title, content, source, category, url, published_date, created_at,
    is_active, compliance_status, engagement_metrics, content_hash,
    approval_timestamp, priority
) VALUES (
    'Retail Expansion Positions High Tide for Long-Term Growth',
    'HITI expands Canna Cabana to 203 stores, boosting market share and outpacing peers with 2.3X revenue per location.',
    'Yahoo Finance',
    'Retail Operations',
    'https://finance.yahoo.com/news/retail-expansion-positions-high-tide-131200011.html',
    '2025-09-02 18:58:00',
    '2025-09-05 01:14:08',
    1,
    'approved',
    '{"business_relevance_score": 5.6000000000000005}',
    'bc8b97113b2c166d58b5e37b1e8f5778',
    '2025-09-05 01:55:13',
    3
);
INSERT INTO content_feeds (
    title, content, source, category, url, published_date, created_at,
    is_active, compliance_status, engagement_metrics, content_hash,
    approval_timestamp, priority
) VALUES (
    'Cannabis Sales Were Soft Again',
    'New Cannabis Ventures offers readers this easy-to-read exclusive summary of BDSA’s monthly cannabis sales data for 15 states. Cannabis sales increased 0.5% sequentially in August, which was a decrease on a per-day basis of 2.7%. In this review, we share the results by state, beginning with the western markets and then concluding with the eastern […]',
    'New Cannabis Ventures',
    'Industry Commentary',
    'https://www.newcannabisventures.com/cannabis-sales-were-soft-again/',
    '2025-09-04 20:01:35',
    '2025-09-05 01:14:08',
    1,
    'approved',
    '{"business_relevance_score": 7.5}',
    'ed335b5e90080b448324d727befb80ed',
    '2025-09-05 01:54:15',
    1
);
INSERT INTO content_feeds (
    title, content, source, category, url, published_date, created_at,
    is_active, compliance_status, engagement_metrics, content_hash,
    approval_timestamp, priority
) VALUES (
    'Texans Evade 3rd Hemp THC Ban Attempt; Legislature Adjourns',
    'The Texas Senate and House adjournedsine diefrom their second special session without agreeing on a path forward for intoxicating THC products.',
    'Cannabis Business Times',
    'Industry Commentary',
    'https://www.cannabisbusinesstimes.com/us-states/texas/news/15754544/texans-evade-3rd-hemp-thc-ban-attempt-legislature-adjourns',
    '2025-09-04 14:15:16',
    '2025-09-05 01:14:08',
    1,
    'approved',
    '{"business_relevance_score": 7.5}',
    '3159600a273d152961d8cd04a70a047b',
    '2025-09-05 01:54:15',
    3
);
INSERT INTO content_feeds (
    title, content, source, category, url, published_date, created_at,
    is_active, compliance_status, engagement_metrics, content_hash,
    approval_timestamp, priority
) VALUES (
    'Cannabis sold in Ontario recalled',
    'Emblem Cannabis Corporation has recalled one lot of Divvy Island Rush Infused Pre-Rolls due to A labelling issue. "Emblem Cannabis Corporation applied the wrong label to the affected product," Health Canada explained in its recall notice.',
    'Inside Halton',
    'Regulatory',
    'https://www.insidehalton.com/news/cannabis-ontario-recall/article_bb7cf238-815a-53e3-b05b-f1542cda1b05.html',
    '2025-09-04 18:34:00',
    '2025-09-05 01:14:08',
    1,
    'approved',
    '{"business_relevance_score": 5.8}',
    'b5ad3d4d0effecbe9ff34399aef81d2e',
    '2025-09-05 01:54:15',
    3
);
INSERT INTO content_feeds (
    title, content, source, category, url, published_date, created_at,
    is_active, compliance_status, engagement_metrics, content_hash,
    approval_timestamp, priority
) VALUES (
    'Former Trump Advisor Kellyanne Conway Is The ''Biggest Champion'' Of Marijuana Rescheduling In President''s ''Inner Circle,'' GOP Congressman Says',
    'President Donald Trump''s former senior advisor Kellyanne Conway has been the "biggest champion" of marijuana rescheduling within the president''s "inner circle," a GOP congressman tells Marijuana Moment.',
    'Marijuana Moment',
    'Industry Commentary',
    'https://www.marijuanamoment.net/former-trump-advisor-kellyanne-conway-is-the-biggest-champion-of-marijuana-rescheduling-in-presidents-inner-circle-gop-congressman-says/',
    '2025-09-04 19:59:00',
    '2025-09-05 01:14:08',
    1,
    'approved',
    '{"business_relevance_score": 5.0}',
    '26d4ac1cc98b3bfd7b27faf4dd9bd3a9',
    '2025-09-05 01:54:15',
    3
);
INSERT INTO content_feeds (
    title, content, source, category, url, published_date, created_at,
    is_active, compliance_status, engagement_metrics, content_hash,
    approval_timestamp, priority
) VALUES (
    'Cannabis sold in Ontario recalled',
    'You may unsubscribe at any time. By signing up, you agree to our terms of use and privacy policy. This site is protected by reCAPTCHA and the Google privacy policy and terms of service apply.',
    'The Hamilton Spectator',
    'Industry Commentary',
    'https://www.thespec.com/news/cannabis-ontario-recall/article_9ee02245-5d79-5595-931b-0c04f6bd86a0.html',
    '2025-09-04 19:08:00',
    '2025-09-05 01:14:08',
    1,
    'approved',
    '{"business_relevance_score": 5.0}',
    'af398113fa5e89df91dee6a06a23e2bd',
    '2025-09-05 01:54:15',
    3
);
INSERT INTO content_feeds (
    title, content, source, category, url, published_date, created_at,
    is_active, compliance_status, engagement_metrics, content_hash,
    approval_timestamp, priority
) VALUES (
    'Customer support with MTL?',
    'Hey I was wondering if the guys at MTL are any reliable when it comes to customer support and complaints. Picked up a 3.5 g of their frosted flakes dessert recently. The bud was so dry it just crumbled into dust. Zero moisture and negligible effects. Wanted to know if they would replace it if I mailed them.',
    'r/TheOCS',
    'Community',
    'https://reddit.com/r/TheOCS/comments/1n3znde/customer_support_with_mtl/',
    '2025-08-30 05:50:42',
    '2025-08-30 14:26:36',
    1,
    'approved',
    '{"business_relevance_score": 4.0}',
    '127e38cea4353b3861dfda4c310bb815',
    '2025-09-01 17:42:17',
    3
);
INSERT INTO content_feeds (
    title, content, source, category, url, published_date, created_at,
    is_active, compliance_status, engagement_metrics, content_hash,
    approval_timestamp, priority
) VALUES (
    '420 With CNW - Google Announces Pilot Program Testing Cannabis Business Advertising In Canada',
    'Google has started testing a new advertising program that gives Canadian cannabis businesses limited access to its ad services, provided they meet fe',
    'MENAFN',
    'Industry Commentary',
    'https://menafn.com/1109995370/420-With-CNW-Google-Announces-Pilot-Program-Testing-Cannabis-Business-Advertising-In-Canada',
    '2025-08-30 03:55:00',
    '2025-08-30 14:56:50',
    1,
    'approved',
    '{"business_relevance_score": 5.0}',
    '4ce8a650953e2257f1c9d6c45141bd0c',
    '2025-09-01 17:42:17',
    3
);
INSERT INTO content_feeds (
    title, content, source, category, url, published_date, created_at,
    is_active, compliance_status, engagement_metrics, content_hash,
    approval_timestamp, priority
) VALUES (
    'OPP bust $8M illicit cannabis operation in Ontario',
    'An eight-month drug investigation by Ontario Provincial Police has resulted in five arrests, including two residents from Brantford, and the seizure of $8 million in illegal cannabis.',
    'CTV News',
    'Industry Commentary',
    'https://www.ctvnews.ca/kitchener/article/opp-bust-8m-illicit-cannabis-operation-in-ontario/',
    '2025-08-29 22:42:00',
    '2025-08-30 15:40:17',
    1,
    'approved',
    '{"business_relevance_score": 5.8}',
    '615f15722264c270a5a87b42f4b85466',
    '2025-09-01 17:42:17',
    4
);
INSERT INTO content_feeds (
    title, content, source, category, url, published_date, created_at,
    is_active, compliance_status, engagement_metrics, content_hash,
    approval_timestamp, priority
) VALUES (
    'Craft Medley Lite N'' Smooth Pre-Rolls by HiFeelU(UFeelU)',
    'Craft Medley Lite N'' Smooth Pre-Rolls by HiFeelU(UFeelU) 

1. Packaging
An opaque plastic tube containing five 0.35g pre-rolls. The label lists the THC (9.87%)/CBD (8.53%)/CBG (0.1%) and total terpenes (1.03%). CBG is a minor cannabinoid similar to CBD in that it is non-psychoactive and has anti-inflammatory and mood-enhancing properties, among others. There''s also a list of dominant terpenes, the',
    'r/TheOCS',
    'Community',
    'https://reddit.com/r/TheOCS/comments/1n5srs4/craft_medley_lite_n_smooth_prerolls_by/',
    '2025-09-01 10:06:29',
    '2025-09-01 17:40:01',
    1,
    'approved',
    '{"business_relevance_score": 5.5}',
    'ada8d58512f5f5237943022bbd855ef0',
    '2025-09-01 17:41:47',
    3
);
INSERT INTO content_feeds (
    title, content, source, category, url, published_date, created_at,
    is_active, compliance_status, engagement_metrics, content_hash,
    approval_timestamp, priority
) VALUES (
    'Anyone know what''s going on with BC Smalls?',
    'Loved this brand when they launched but lately they''ve falling off. Recently purchased their White OG and the buds were brown. Bought Sonic Screwdriver and the buds were purple, no lemon scent. Just bought Hippie Cripwalk and this batch is legit their Sonic Screwdriver. Wtf🫠',
    'r/TheOCS',
    'Community',
    'https://reddit.com/r/TheOCS/comments/1n5td94/anyone_know_whats_going_on_with_bc_smalls/',
    '2025-09-01 10:28:42',
    '2025-09-01 17:40:01',
    1,
    'approved',
    '{"business_relevance_score": 4.0}',
    '8387265e03b9505d9c6361b18a595d29',
    '2025-09-01 17:41:47',
    3
);
INSERT INTO content_feeds (
    title, content, source, category, url, published_date, created_at,
    is_active, compliance_status, engagement_metrics, content_hash,
    approval_timestamp, priority
) VALUES (
    'LOT420 Gelato 33 10/10 🔥 AAAA',
    'amazing taste and perfect burn ✔️ ',
    'r/TheOCS',
    'Community',
    'https://reddit.com/r/TheOCS/comments/1n5tbch/lot420_gelato_33_1010_aaaa/',
    '2025-09-01 10:26:38',
    '2025-09-01 17:40:01',
    1,
    'approved',
    '{"business_relevance_score": 2.7}',
    'f700d22d6c9fe2ce138b50dfb269afbb',
    '2025-09-01 17:41:47',
    3
);
INSERT INTO content_feeds (
    title, content, source, category, url, published_date, created_at,
    is_active, compliance_status, engagement_metrics, content_hash,
    approval_timestamp, priority
) VALUES (
    'canadian cannabis',
    'CHCH-TV started broadcasting in 1954 and is proud to be the news leader for Hamilton and the surrounding Halton and Niagara regions.',
    'CHCH TV',
    'Industry Commentary',
    'https://www.chch.com/tag/canadian-cannabis/',
    '2025-09-01 09:38:00',
    '2025-09-01 17:40:01',
    1,
    'approved',
    '{"business_relevance_score": 5.0}',
    'bebba67ec7164049850a094ee584938e',
    '2025-09-01 17:41:47',
    4
);

-- End of export
