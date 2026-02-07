const axios = require('axios');
const chalk = require('chalk');
const fs = require('fs');
const path = require('path');

// Results directory
const RESULTS_DIR = path.resolve(__dirname, '../results/reddit');

// Default movie query
const args = process.argv.slice(2);
const MOVIE_QUERY = args.length > 0 ? args.join(' ') : "One Battle After Another";

// Subreddits to search
const SUBREDDITS = ['movies', 'oscarrace', 'boxoffice', 'trailers', 'flicks'];

// Rate limit delay (Reddit requires ~1 second between requests)
const DELAY_MS = 1200;

const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));

async function searchSubreddit(subreddit, query) {
    const url = `https://www.reddit.com/r/${subreddit}/search.json`;

    try {
        const response = await axios.get(url, {
            params: {
                q: query,
                restrict_sr: 'on',
                sort: 'relevance',
                limit: 25
            },
            headers: {
                'User-Agent': 'oscars-analytics/1.0 (educational project)'
            }
        });

        if (!response.data.data || !response.data.data.children) {
            return [];
        }

        return response.data.data.children.map(post => ({
            id: post.data.id,
            title: post.data.title,
            subreddit: post.data.subreddit,
            url: `https://reddit.com${post.data.permalink}`,
            score: post.data.score,
            numComments: post.data.num_comments,
            created: new Date(post.data.created_utc * 1000).toISOString()
        }));
    } catch (error) {
        if (error.response?.status === 429) {
            console.log(chalk.yellow(`   ⏳ Rate limited on r/${subreddit}, waiting...`));
            await sleep(5000);
            return searchSubreddit(subreddit, query); // Retry
        }
        console.error(chalk.red(`   ❌ Error searching r/${subreddit}: ${error.message}`));
        return [];
    }
}

async function getPostComments(postId, subreddit) {
    const url = `https://www.reddit.com/r/${subreddit}/comments/${postId}.json`;

    try {
        const response = await axios.get(url, {
            params: { limit: 100, depth: 5 },
            headers: {
                'User-Agent': 'oscars-analytics/1.0 (educational project)'
            }
        });

        const comments = [];

        function extractComments(children) {
            if (!children) return;
            for (const child of children) {
                if (child.kind === 't1' && child.data.body) {
                    comments.push({
                        body: child.data.body,
                        score: child.data.score,
                        created: new Date(child.data.created_utc * 1000).toISOString()
                    });
                    if (child.data.replies?.data?.children) {
                        extractComments(child.data.replies.data.children);
                    }
                }
            }
        }

        if (response.data[1]?.data?.children) {
            extractComments(response.data[1].data.children);
        }

        return comments;
    } catch (error) {
        if (error.response?.status === 429) {
            console.log(chalk.yellow(`   ⏳ Rate limited, waiting...`));
            await sleep(5000);
            return getPostComments(postId, subreddit);
        }
        return [];
    }
}

function saveResults(data, query) {
    const timestamp = new Date().toISOString().split('T')[0];
    const safeQuery = query.replace(/[^a-zA-Z0-9]/g, '_').substring(0, 30);
    const filename = path.join(RESULTS_DIR, `reddit_${safeQuery}_${timestamp}.json`);

    if (!fs.existsSync(RESULTS_DIR)) {
        fs.mkdirSync(RESULTS_DIR, { recursive: true });
    }

    fs.writeFileSync(filename, JSON.stringify(data, null, 2));
    console.log(chalk.green(`\n📝 Saved to: ${filename}`));
    return filename;
}

async function main() {
    console.log(chalk.cyan('🔴 REDDIT COMMENTS FETCHER 🔴'));
    console.log(chalk.gray('----------------------------------------------'));
    console.log(chalk.blue(`🔍 Searching for: "${MOVIE_QUERY}"\n`));

    const allPosts = [];
    const commentsByVideo = {};

    // Search each subreddit
    for (const subreddit of SUBREDDITS) {
        process.stdout.write(chalk.gray(`   Searching r/${subreddit}... `));
        const posts = await searchSubreddit(subreddit, MOVIE_QUERY);
        console.log(chalk.green(`Found ${posts.length} posts`));
        allPosts.push(...posts);
        await sleep(DELAY_MS);
    }

    if (allPosts.length === 0) {
        console.log(chalk.red('\nNo posts found.'));
        return;
    }

    // Sort by score and take top posts
    const topPosts = allPosts
        .sort((a, b) => b.score - a.score)
        .filter(p => p.numComments > 0)
        .slice(0, 15);

    console.log(chalk.blue(`\n💬 Fetching comments from top ${topPosts.length} posts...\n`));

    let totalComments = 0;
    for (const post of topPosts) {
        process.stdout.write(chalk.gray(`   "${post.title.substring(0, 50)}..." `));
        const comments = await getPostComments(post.id, post.subreddit);
        // Store just the comment bodies like YouTube format
        commentsByVideo[post.title] = comments.map(c => c.body);
        totalComments += comments.length;
        console.log(chalk.green(`${comments.length} comments`));
        await sleep(DELAY_MS);
    }

    // Match YouTube schema format
    const outputData = {
        query: MOVIE_QUERY,
        fetchedAt: new Date().toISOString(),
        totalComments: totalComments,
        videoCount: topPosts.length,
        commentsByVideo: commentsByVideo
    };

    console.log(chalk.blue(`\n📦 Total: ${totalComments} comments from ${topPosts.length} posts`));
    saveResults(outputData, MOVIE_QUERY);
}

main().catch(console.error);
