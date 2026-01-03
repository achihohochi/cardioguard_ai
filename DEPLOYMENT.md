# CardioGuard_AI - Render Deployment Guide

This guide walks you through deploying CardioGuard_AI to Render hosting platform.

## Prerequisites

- Render account (you have one)
- GitHub repository with CardioGuard_AI code pushed
- Anthropic API key (required)
- Pinecone API key (optional, for vector database features)

## Quick Start

1. **Push code to GitHub** (if not already done)
   ```bash
   git add .
   git commit -m "Add Render deployment configuration"
   git push origin main
   ```

2. **Deploy via Render Dashboard** (see detailed steps below)

## Detailed Deployment Steps

### Step 1: Prepare Your Repository

Ensure all code is committed and pushed to GitHub:

```bash
cd CardioGuard_AI
git status  # Check for uncommitted changes
git add .
git commit -m "Prepare for Render deployment"
git push origin main
```

**Important**: Verify that `.env` is in `.gitignore` (it should be already).

### Step 2: Create Render Web Service

1. **Log into Render Dashboard**
   - Go to [render.com](https://render.com)
   - Sign in with your account

2. **Create New Web Service**
   - Click the **"New +"** button in the top right
   - Select **"Web Service"**

3. **Connect Repository**
   - Click **"Connect account"** if you haven't connected GitHub yet
   - Authorize Render to access your GitHub repositories
   - Select your GitHub account
   - Find and select the `CardioGuard_AI` repository
   - Click **"Connect"**

### Step 3: Configure Service Settings

Render will auto-detect the `render.yaml` file, but you can also configure manually:

**Basic Settings:**
- **Name**: `cardioguard-ai` (or your preferred name)
- **Region**: Choose closest to your users (e.g., `Oregon (US West)` or `Frankfurt (EU)`)
- **Branch**: `main` (or your default branch)
- **Root Directory**: (leave empty - root is fine)

**Build & Deploy:**
- **Environment**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `streamlit run app.py --server.port=$PORT --server.address=0.0.0.0 --server.headless=true`

**Note**: If you're using `render.yaml`, these will be auto-filled.

### Step 4: Set Environment Variables

In the Render dashboard, navigate to your service → **Environment** section:

**Required Variables:**
- `ANTHROPIC_API_KEY` - Your Anthropic Claude API key (get from [console.anthropic.com](https://console.anthropic.com/))

**Optional Variables:**
- `PINECONE_API_KEY` - Pinecone vector database API key (optional)
- `PINECONE_ENVIRONMENT` - Pinecone environment name (optional)
- `WEB_SEARCH_ENABLED` - Set to `true` or `false` (default: `true`)
- `LOG_LEVEL` - Logging level: `DEBUG`, `INFO`, `WARNING`, `ERROR` (default: `INFO`)

**How to Add:**
1. Click **"Add Environment Variable"**
2. Enter the key name (e.g., `ANTHROPIC_API_KEY`)
3. Enter the value
4. Click **"Save Changes"**

**Important**: Never commit API keys to git. Always use Render's environment variables.

### Step 5: Deploy

1. **Review Settings**
   - Double-check all configuration
   - Verify environment variables are set

2. **Create Web Service**
   - Click **"Create Web Service"** at the bottom
   - Render will start building your application

3. **Monitor Build**
   - Watch the build logs in real-time
   - First deployment takes 5-10 minutes
   - Subsequent deployments are faster (~2-3 minutes)

### Step 6: Access Your Application

Once deployment completes:

1. **Get Your URL**
   - Render provides a URL like: `https://cardioguard-ai.onrender.com`
   - This URL is available immediately

2. **Test the Application**
   - Open the URL in your browser
   - Test with a known provider NPI: `1992796015`
   - Verify all features work:
     - Provider analysis completes
     - Risk score displays correctly
     - PDF export works
     - Data sources show status

## Post-Deployment Checklist

- [ ] App builds successfully on Render
- [ ] App starts without errors
- [ ] Environment variables are loaded correctly
- [ ] API calls work (Anthropic API)
- [ ] Provider analysis completes successfully (~30 seconds)
- [ ] PDF export works
- [ ] Web search functionality works (if enabled)
- [ ] App handles errors gracefully
- [ ] Test with NPI `1992796015` (known excluded provider)

## Troubleshooting

### Build Failures

**Issue**: Build fails with dependency errors
- **Solution**: Check `requirements.txt` for version conflicts
- Verify Python version in `runtime.txt` matches Render's Python 3.11

**Issue**: Import errors during build
- **Solution**: Ensure all Python files are committed to git
- Check that `__init__.py` files exist in `agents/` and `services/` directories

### Runtime Errors

**Issue**: Port binding errors
- **Solution**: Verify start command includes `--server.address=0.0.0.0`
- Check that `$PORT` environment variable is used

**Issue**: Environment variables not loading
- **Solution**: Verify variables are set in Render dashboard → Environment
- Check variable names match exactly (case-sensitive)
- Restart the service after adding new variables

**Issue**: API errors (Anthropic API)
- **Solution**: Verify `ANTHROPIC_API_KEY` is set correctly
- Check API key is valid and has credits
- Review logs for specific error messages

**Issue**: App sleeps after inactivity (free tier)
- **Solution**: This is normal for Render free tier
- App wakes up automatically when accessed (takes ~30 seconds)
- Consider upgrading to paid plan for always-on service

### Performance Issues

**Issue**: Analysis takes longer than 30 seconds
- **Solution**: Check Render service logs for timeouts
- Verify API response times
- Consider upgrading to paid plan for better resources

**Issue**: App crashes under load
- **Solution**: Free tier has resource limits
- Consider upgrading to paid plan for production use

## Render Free Tier Limitations

- **750 hours/month** of runtime
- **512MB RAM** per service
- **Sleep after 15 minutes** of inactivity
- **~30 second wake time** when sleeping
- **No custom domain** (free tier)
- **Shared resources** (may be slower during peak times)

## Upgrading to Paid Plan

For production use, consider upgrading:

- **Starter Plan**: $7/month
  - Always-on service (no sleep)
  - 512MB RAM
  - Custom domain support
  
- **Standard Plan**: $25/month
  - Always-on service
  - 2GB RAM
  - Better performance
  - Custom domain + SSL

## Monitoring & Logs

### View Logs

1. Go to Render dashboard
2. Select your service
3. Click **"Logs"** tab
4. View real-time logs or download log files

### Monitor Performance

- Check **Metrics** tab for:
  - CPU usage
  - Memory usage
  - Request count
  - Response times

### Set Up Alerts

1. Go to **Settings** → **Alerts**
2. Configure email alerts for:
   - Deployment failures
   - Service crashes
   - High resource usage

## Custom Domain (Paid Plans)

1. Go to **Settings** → **Custom Domains**
2. Add your domain
3. Follow DNS configuration instructions
4. SSL certificate is automatically provisioned

## Cost Estimation

**Render Hosting:**
- Free tier: $0/month (with limitations)
- Starter: $7/month (always-on)

**API Costs (Your Responsibility):**
- Anthropic Claude API: ~$0.01-0.05 per analysis
- Estimated monthly cost: <$5 for moderate usage
- Pinecone: Free tier available (optional)

**Total Estimated Cost:**
- Free tier: ~$0-5/month (API usage only)
- Starter plan: ~$7-12/month (hosting + API)

## Security Best Practices

1. **Never commit secrets** to git
2. **Use Render environment variables** for all API keys
3. **Rotate API keys** periodically
4. **Monitor API usage** in Anthropic dashboard
5. **Set up alerts** for unusual activity
6. **Review logs** regularly for errors

## Rollback Deployment

If something goes wrong:

1. Go to **Deploys** tab
2. Find the last working deployment
3. Click **"Rollback"**
4. Service will revert to that version

## Continuous Deployment

Render automatically deploys when you push to your connected branch:

1. Push code to GitHub
2. Render detects changes
3. Builds new version
4. Deploys automatically
5. Sends notification email

To disable auto-deploy:
- Go to **Settings** → **Auto-Deploy**
- Toggle off

## Support Resources

- **Render Documentation**: [render.com/docs](https://render.com/docs)
- **Render Status**: [status.render.com](https://status.render.com)
- **Render Community**: [community.render.com](https://community.render.com)
- **Streamlit Deployment**: [docs.streamlit.io/deploy](https://docs.streamlit.io/deploy)

## Next Steps

After successful deployment:

1. **Test thoroughly** with multiple provider NPIs
2. **Monitor performance** and costs
3. **Set up custom domain** (if using paid plan)
4. **Configure alerts** for production monitoring
5. **Document your deployment** for team members

---

**Congratulations!** Your CardioGuard_AI application is now publicly accessible on Render.

For questions or issues, check the troubleshooting section above or consult Render's documentation.
