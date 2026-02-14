const axios = require('axios');
const cheerio = require('cheerio');
const chalk = require('chalk');
const fs = require('fs');
const path = require('path');

// Results directory
const RESULTS_DIR = path.resolve(__dirname, '../results/twitter');

// Default movie query
const args = process.argv.slice(2);
const MOVIE_QUERY = args.length > 0 ? args.join(' ') : "One Battle After Another";

// List of Nitter instances to try (these change frequently)
const NITTER_INSTANCES = [
    'https://nitter.net',
    'https://nitter.cz',
    'https://nitter.hu',
    'https://nitter.esmailelbob.xyz',
    'https://nitter.lucabased.xyz',
    'https://nitter.rawbit.ninja',
    'https://nitter.tux.pizza',
    'https://nitter.d420.de',
    'https://nitter.lunar.icu',
    'https://nitter.sneed.network'
];

const DELAY_MS = 2000;
const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));

async function findWorkingInstance() {
    console.log(chalk.blue('🔍 Finding a working Nitter instance...\n'));

    for (const instance of NITTER_INSTANCES) {
        try {
            process.stdout.write(chalk.gray(`   Testing ${instance}... `));
            const response = await axios.get(instance, {
                timeout: 10000,
                headers: {
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
                }
            });
            if (response.status === 200) {
                console.log(chalk.green('✓ Working!'));
                return instance;
            }
        } catch (error) {
            console.log(chalk.red('✗ Down'));
        }
    }
    return null;
}

async function searchTweets(instance, query, maxPages = 3) {
    const tweets = [];
    const encodedQuery = encodeURIComponent(query);
    let cursor = '';

    for (let page = 0; page < maxPages; page++) {
        try {
            const url = cursor
                ? `${instance}/search?f=tweets&q=${encodedQuery}&cursor=${cursor}`
                : `${instance}/search?f=tweets&q=${encodedQuery}`;

            process.stdout.write(chalk.gray(`   Fetching page ${page + 1}... `));

            const response = await axios.get(url, {
                timeout: 15000,
                headers: {
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                    'Accept': 'text/html,application/xhtml+xml',
                    'Accept-Language': 'en-US,en;q=0.9'
                }
            });

            const $ = cheerio.load(response.data);

            // Extract tweets from the page
            $('.timeline-item').each((i, el) => {
                const tweetContent = $(el).find('.tweet-content').text().trim();
                const username = $(el).find('.username').first().text().trim();
                const date = $(el).find('.tweet-date a').attr('title') || '';
                const stats = $(el).find('.tweet-stat');

                if (tweetContent && tweetContent.length > 0) {
                    tweets.push({
                        text: tweetContent,
                        username: username,
                        date: date
                    });
                }
            });

            // Find next page cursor
            const showMore = $('.show-more:last-child a').attr('href');
            if (showMore) {
                const cursorMatch = showMore.match(/cursor=([^&]+)/);
                cursor = cursorMatch ? cursorMatch[1] : '';
            } else {
                cursor = '';
            }

            console.log(chalk.green(`Got ${tweets.length} tweets so far`));

            if (!cursor) {
                console.log(chalk.yellow('   No more pages available'));
                break;
            }

            await sleep(DELAY_MS);
        } catch (error) {
            console.log(chalk.red(`Error: ${error.message}`));
            break;
        }
    }

    return tweets;
}

function saveResults(tweets, query) {
    const timestamp = new Date().toISOString().split('T')[0];
    const safeQuery = query.replace(/[^a-zA-Z0-9]/g, '_').substring(0, 30);
    const filename = path.join(RESULTS_DIR, `twitter_${safeQuery}_${timestamp}.json`);

    if (!fs.existsSync(RESULTS_DIR)) {
        fs.mkdirSync(RESULTS_DIR, { recursive: true });
    }

    // Match YouTube/Reddit schema format
    const outputData = {
        query: query,
        fetchedAt: new Date().toISOString(),
        totalComments: tweets.length,
        videoCount: 1,  // Twitter doesn't have video grouping like YT/Reddit
        commentsByVideo: {
            [`Twitter Search: ${query}`]: tweets.map(t => t.text)
        }
    };

    fs.writeFileSync(filename, JSON.stringify(outputData, null, 2));
    console.log(chalk.green(`\n📝 Saved to: ${filename}`));
    return filename;
}

async function main() {
    console.log(chalk.cyan('🐦 TWITTER/NITTER SCRAPER 🐦'));
    console.log(chalk.gray('----------------------------------------------'));
    console.log(chalk.blue(`Query: "${MOVIE_QUERY}"\n`));

    // Find a working Nitter instance
    const instance = await findWorkingInstance();

    if (!instance) {
        console.log(chalk.red('\n❌ No working Nitter instances found.'));
        console.log(chalk.yellow('All public Nitter instances may be down or blocked.'));
        console.log(chalk.yellow('You can try again later or check: https://github.com/zedeus/nitter/wiki/Instances'));
        return;
    }

    console.log(chalk.green(`\n✓ Using: ${instance}\n`));
    console.log(chalk.blue('💬 Searching for tweets...\n'));

    const tweets = await searchTweets(instance, MOVIE_QUERY, 5);

    if (tweets.length === 0) {
        console.log(chalk.red('\nNo tweets found.'));
        console.log(chalk.yellow('The Nitter instance might be rate-limited or the search returned no results.'));
        return;
    }

    console.log(chalk.blue(`\n📦 Total: ${tweets.length} tweets`));
    saveResults(tweets, MOVIE_QUERY);
}

main().catch(console.error);
