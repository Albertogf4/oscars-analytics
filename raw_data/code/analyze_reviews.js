// Try to load .env, with fallback for permission issues
try {
    require('dotenv').config({ path: require('path').resolve(__dirname, '.env') });
} catch (e) {
    console.log('Note: Could not load .env file, using environment variables');
}
const axios = require('axios');
const Sentiment = require('sentiment');
const chalk = require('chalk');
const fs = require('fs');
const path = require('path');

// Results directory (../results relative to this script)
const RESULTS_DIR = path.resolve(__dirname, '../results');

const sentiment = new Sentiment();

// Try environment variable, then fall back if needed
const YOUTUBE_API_KEY = process.env.YOUTUBE_API_KEY;

// Default to "One Battle After Another" if no argument provided
const args = process.argv.slice(2);
const MOVIE_QUERY = args.length > 0 ? args.join(' ') : "One Battle After Another trailer";

const TOTAL_COMMENT_TARGET = 1000;
const MAX_VIDEOS = 5;

// Mock data for when API key is missing
const MOCK_COMMENTS = [
    "One Battle After Another looks intense! The war scenes are realistic.",
    "Finally a movie about this historical event.",
    "The cinematography is breathtaking, but the dialogue seems a bit cheesy.",
    "I hope they respect the source material.",
    "Music gives me chills.",
    "Looks like another generic war movie.",
    "Cannot wait to see this in theaters.",
    "The acting seems top tier.",
    "Why does every trailer reveal the whole plot?",
    "Oscar contender for sure!"
];

async function searchVideos() {
    console.log(chalk.blue(`🔍 Searching for top ${MAX_VIDEOS} videos: "${MOVIE_QUERY}"...`));
    console.log(chalk.gray('   (Cost: 100 API units)'));

    if (!YOUTUBE_API_KEY || YOUTUBE_API_KEY === 'YOUR_NEW_KEY_HERE') {
        if (!process.env.YOUTUBE_API_KEY) {
            console.log(chalk.yellow('⚠️  No YOUTUBE_API_KEY found in .env file (it is empty or missing)'));
        } else {
            console.log(chalk.yellow('⚠️  YOUTUBE_API_KEY is still set to placeholder text in .env'));
        }
        console.log(chalk.yellow('   Using MOCK MODE (simulated data)'));
        return ['MOCK_VIDEO_ID'];
    }

    try {
        const response = await axios.get('https://www.googleapis.com/youtube/v3/search', {
            params: {
                part: 'snippet',
                q: MOVIE_QUERY,
                key: YOUTUBE_API_KEY,
                type: 'video',
                maxResults: MAX_VIDEOS
            }
        });

        if (!response.data.items || response.data.items.length === 0) throw new Error('No videos found');

        const videos = response.data.items.map(item => ({
            id: item.id.videoId,
            title: item.snippet.title,
            channel: item.snippet.channelTitle
        }));

        videos.forEach((v, i) => console.log(chalk.green(`   ${i + 1}. Found: "${v.title}" (${v.channel})`)));
        return videos; // Return array of objects {id, title}
    } catch (error) {
        console.error(chalk.red('❌ Search failed:'), error.message);
        if (error.response) console.error(chalk.red('   API Error:'), error.response.data.error.message);
        return [];
    }
}

async function getCommentsForVideo(videoId, targetCount) {
    if (videoId === 'MOCK_VIDEO_ID') {
        return MOCK_COMMENTS;
    }

    let comments = [];
    let nextPageToken = '';
    let pageCount = 0;

    // Safety limit to prevent infinite loops or excessive quota usage
    const MAX_PAGES = Math.ceil(targetCount / 100) + 1;

    try {
        while (comments.length < targetCount && pageCount < MAX_PAGES) {
            const response = await axios.get('https://www.googleapis.com/youtube/v3/commentThreads', {
                params: {
                    part: 'snippet',
                    videoId: videoId,
                    key: YOUTUBE_API_KEY,
                    maxResults: 100, // API max per page
                    textFormat: 'plainText',
                    pageToken: nextPageToken || undefined
                }
            });

            const newComments = response.data.items.map(item => item.snippet.topLevelComment.snippet.textDisplay);
            comments = comments.concat(newComments);

            nextPageToken = response.data.nextPageToken;
            pageCount++;

            process.stdout.write(chalk.gray(`.`)); // Progress dot

            if (!nextPageToken) break;
        }
        return comments;
    } catch (error) {
        // If comments are disabled or other error, just return what we have
        // console.error(chalk.red(`   ❌ Error fetching comments for ${videoId}: ${error.message}`));
        return comments;
    }
}

function saveCommentsToJson(commentsByVideo) {
    const timestamp = new Date().toISOString().split('T')[0];
    const filename = path.join(RESULTS_DIR, `comments_${timestamp}.json`);

    const outputData = {
        query: MOVIE_QUERY,
        fetchedAt: new Date().toISOString(),
        totalComments: Object.values(commentsByVideo).flat().length,
        videoCount: Object.keys(commentsByVideo).length,
        commentsByVideo: commentsByVideo
    };

    // Ensure results directory exists
    if (!fs.existsSync(RESULTS_DIR)) {
        fs.mkdirSync(RESULTS_DIR, { recursive: true });
    }

    try {
        fs.writeFileSync(filename, JSON.stringify(outputData, null, 2));
        console.log(chalk.green(`\n📝 Comments saved to: ${filename}`));
        console.log(chalk.cyan(`   Total comments: ${outputData.totalComments}`));
        console.log(chalk.cyan(`   Videos indexed: ${outputData.videoCount}`));
    } catch (err) {
        console.error(chalk.red(`❌ Failed to save comments: ${err.message}`));
    }
}

async function main() {
    console.log(chalk.cyan('� YOUTUBE COMMENTS FETCHER �'));
    console.log(chalk.gray('----------------------------------------------'));

    const videos = await searchVideos();
    if (videos.length === 0) return;

    // Object to store comments indexed by video title
    const commentsByVideo = {};

    // Calculate how many comments to fetch per video to reach total target roughly
    const targetPerVideo = Math.ceil(TOTAL_COMMENT_TARGET / videos.length);

    console.log(chalk.blue(`💬 Fetching up to ~${TOTAL_COMMENT_TARGET} comments total (${targetPerVideo} per video)...`));

    for (const video of videos) {
        // If it's a mock ID handle it directly in getCommentsForVideo, otherwise pass ID
        const finalId = typeof video === 'string' ? video : video.id;
        const videoTitle = video.title || 'Mock Video';

        process.stdout.write(chalk.gray(`   Fetching for "${videoTitle}" `));

        const vidComments = await getCommentsForVideo(finalId, targetPerVideo);

        // Index by video title
        commentsByVideo[videoTitle] = vidComments;

        console.log(chalk.green(` ✅ Got ${vidComments.length} comments`));
    }

    const totalComments = Object.values(commentsByVideo).flat().length;
    if (totalComments === 0) {
        console.log(chalk.red('No comments found.'));
        return;
    }

    console.log(chalk.blue(`\n📦 Saving ${totalComments} comments to JSON...`));
    saveCommentsToJson(commentsByVideo);
}

main();
