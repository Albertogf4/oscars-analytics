const axios = require('axios');
const cheerio = require('cheerio');
const chalk = require('chalk');
const fs = require('fs');
const path = require('path');

// Results directory
const RESULTS_DIR = path.resolve(__dirname, '../results/letterboxd');

// Movie slugs mapping (Letterboxd uses URL slugs)
const MOVIE_SLUGS = {
    'One Battle After Another': 'one-battle-after-another',
    'Sinners': 'sinners',
    'F1': 'f1-2025',
    'Marty Supreme': 'marty-supreme'
};

// Default movie
const args = process.argv.slice(2);
const MOVIE_NAME = args.length > 0 ? args.join(' ') : "Sinners";

const DELAY_MS = 1500;
const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));

// Headers to mimic a real browser
const HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Cache-Control': 'no-cache',
    'Pragma': 'no-cache',
    'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
    'Sec-Ch-Ua-Mobile': '?0',
    'Sec-Ch-Ua-Platform': '"macOS"',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1'
};

async function fetchReviewsPage(slug, page = 1) {
    const url = page === 1
        ? `https://letterboxd.com/film/${slug}/reviews/`
        : `https://letterboxd.com/film/${slug}/reviews/page/${page}/`;

    try {
        const response = await axios.get(url, {
            headers: HEADERS,
            timeout: 15000
        });

        return response.data;
    } catch (error) {
        if (error.response?.status === 403) {
            console.log(chalk.yellow(`   ⚠️ Access blocked (403). Letterboxd may be rate-limiting.`));
        } else if (error.response?.status === 404) {
            console.log(chalk.yellow(`   ⚠️ Page not found (404).`));
        } else {
            console.log(chalk.red(`   ❌ Error: ${error.message}`));
        }
        return null;
    }
}

function parseReviews(html) {
    const $ = cheerio.load(html);
    const reviews = [];

    // Letterboxd review structure
    $('.film-detail').each((i, el) => {
        const reviewText = $(el).find('.body-text p').text().trim();
        const rating = $(el).find('.rating').text().trim();
        const username = $(el).find('.name').text().trim();

        if (reviewText && reviewText.length > 0) {
            reviews.push({
                text: reviewText,
                rating: rating || 'No rating',
                username: username
            });
        }
    });

    // Also try alternate selectors
    if (reviews.length === 0) {
        $('li.film-detail, div.review').each((i, el) => {
            const reviewText = $(el).find('div.body-text, .review-body').text().trim();
            if (reviewText && reviewText.length > 0) {
                reviews.push({
                    text: reviewText,
                    rating: '',
                    username: ''
                });
            }
        });
    }

    // Check if there's a next page
    const hasNextPage = $('a.next').length > 0;

    return { reviews, hasNextPage };
}

async function fetchAllReviews(movieName, maxPages = 5) {
    const slug = MOVIE_SLUGS[movieName] || movieName.toLowerCase().replace(/\s+/g, '-');
    console.log(chalk.blue(`   Using slug: "${slug}"`));

    const allReviews = [];

    for (let page = 1; page <= maxPages; page++) {
        process.stdout.write(chalk.gray(`   Fetching page ${page}... `));

        const html = await fetchReviewsPage(slug, page);

        if (!html) {
            console.log(chalk.red('Failed'));
            break;
        }

        const { reviews, hasNextPage } = parseReviews(html);
        allReviews.push(...reviews);

        console.log(chalk.green(`Got ${reviews.length} reviews (total: ${allReviews.length})`));

        if (!hasNextPage || reviews.length === 0) {
            console.log(chalk.yellow('   No more pages'));
            break;
        }

        await sleep(DELAY_MS);
    }

    return allReviews;
}

function saveResults(reviews, movieName) {
    const timestamp = new Date().toISOString().split('T')[0];
    const safeQuery = movieName.replace(/[^a-zA-Z0-9]/g, '_').substring(0, 30);
    const filename = path.join(RESULTS_DIR, `letterboxd_${safeQuery}_${timestamp}.json`);

    if (!fs.existsSync(RESULTS_DIR)) {
        fs.mkdirSync(RESULTS_DIR, { recursive: true });
    }

    // Match YouTube/Reddit schema format
    const outputData = {
        query: movieName,
        fetchedAt: new Date().toISOString(),
        totalComments: reviews.length,
        videoCount: 1,
        commentsByVideo: {
            [`Letterboxd: ${movieName}`]: reviews.map(r => r.text)
        }
    };

    fs.writeFileSync(filename, JSON.stringify(outputData, null, 2));
    console.log(chalk.green(`\n📝 Saved to: ${filename}`));
    return filename;
}

async function main() {
    console.log(chalk.cyan('🎬 LETTERBOXD REVIEW SCRAPER 🎬'));
    console.log(chalk.gray('----------------------------------------------'));
    console.log(chalk.blue(`Movie: "${MOVIE_NAME}"\n`));

    console.log(chalk.blue('💬 Fetching reviews from Letterboxd...\n'));

    const reviews = await fetchAllReviews(MOVIE_NAME, 10);

    if (reviews.length === 0) {
        console.log(chalk.red('\nNo reviews found.'));
        console.log(chalk.yellow('Letterboxd may be blocking requests or the movie slug is incorrect.'));
        console.log(chalk.yellow(`Try checking: https://letterboxd.com/film/${MOVIE_SLUGS[MOVIE_NAME] || MOVIE_NAME.toLowerCase().replace(/\s+/g, '-')}/reviews/`));
        return;
    }

    console.log(chalk.blue(`\n📦 Total: ${reviews.length} reviews`));
    saveResults(reviews, MOVIE_NAME);
}

main().catch(console.error);
