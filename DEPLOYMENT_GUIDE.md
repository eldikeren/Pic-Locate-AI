# PicLocate V4 Deployment Guide

## 🚀 Vercel Deployment

### Prerequisites

1. **Vercel Account**: Sign up at [vercel.com](https://vercel.com)
2. **Vercel CLI**: Install globally
   ```bash
   npm i -g vercel
   ```

### Step 1: Environment Variables

Set up the following environment variables in Vercel:

```bash
# Required
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key

# Optional (for production search)
OPENAI_API_KEY=your-openai-api-key

# Google Drive (for indexing)
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
```

### Step 2: Deploy to Vercel

1. **Login to Vercel**
   ```bash
   vercel login
   ```

2. **Deploy the project**
   ```bash
   vercel --prod
   ```

3. **Set environment variables in Vercel dashboard**
   - Go to your project settings
   - Navigate to Environment Variables
   - Add all required variables

### Step 3: Configure Vercel

The `vercel.json` file is already configured with:
- Python backend routing
- Next.js frontend routing
- Environment variable mapping
- Function timeout settings

## 🔧 Alternative Deployment Options

### Railway

1. **Connect GitHub repository**
2. **Set environment variables**
3. **Deploy automatically**

### Heroku

1. **Create Heroku app**
   ```bash
   heroku create piclocate-v4
   ```

2. **Set environment variables**
   ```bash
   heroku config:set SUPABASE_URL=your-url
   heroku config:set SUPABASE_KEY=your-key
   # ... other variables
   ```

3. **Deploy**
   ```bash
   git push heroku master
   ```

### DigitalOcean App Platform

1. **Create new app from GitHub**
2. **Configure environment variables**
3. **Deploy**

## 📊 Post-Deployment

### Health Check

Visit your deployed URL + `/health` to verify:
- Backend is running
- Database connection is working
- All components are healthy

### API Documentation

Visit your deployed URL + `/docs` for:
- Interactive API documentation
- Endpoint testing
- Request/response examples

### Frontend

The frontend will be available at your main domain with:
- AI search interface
- Real-time indexing status
- System statistics dashboard

## 🔍 Testing Deployment

### 1. Health Check
```bash
curl https://your-domain.vercel.app/health
```

### 2. API Test
```bash
curl https://your-domain.vercel.app/stats/overview
```

### 3. Frontend Test
Visit your domain in a browser and test:
- Search functionality
- Status monitoring
- System statistics

## 🛠️ Troubleshooting

### Common Issues

1. **Environment Variables Not Set**
   - Check Vercel dashboard
   - Verify variable names match code

2. **Database Connection Failed**
   - Verify Supabase URL and key
   - Check database permissions

3. **OpenAI API Errors**
   - Verify API key is valid
   - Check usage limits

4. **Google Drive Authentication**
   - Verify client ID and secret
   - Check OAuth redirect URIs

### Debug Mode

Enable debug logging by setting:
```bash
DEBUG=true
```

## 📈 Monitoring

### Vercel Analytics

- Built-in performance monitoring
- Real-time usage statistics
- Error tracking

### Custom Monitoring

- Health check endpoint: `/health`
- System stats: `/stats/overview`
- Indexing status: `/indexing/status`

## 🔄 Updates

### Automatic Deployments

Vercel automatically deploys when you push to the main branch.

### Manual Deployments

```bash
vercel --prod
```

### Environment Variable Updates

Update in Vercel dashboard and redeploy.

## 🎯 Production Checklist

- [ ] Environment variables configured
- [ ] Database connection working
- [ ] Health check passing
- [ ] Frontend loading correctly
- [ ] Search functionality working
- [ ] Monitoring set up
- [ ] Error tracking enabled
- [ ] Performance optimized

## 📞 Support

For deployment issues:
1. Check Vercel logs
2. Verify environment variables
3. Test endpoints individually
4. Check database connectivity
5. Review error messages

## 🎉 Success!

Once deployed, your PicLocate V4 system will be:
- ✅ Accessible worldwide
- ✅ Auto-scaling
- ✅ Production-ready
- ✅ Monitored and secure
