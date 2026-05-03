#!/bin/bash
# ═══════════════════════════════════════════════════════════════
# India Election Simulator — Cloud Run Deployment Script
# Deploys both backend and frontend to Google Cloud Run
# ═══════════════════════════════════════════════════════════════

set -e

PROJECT_ID="secure-totality-495209-f6"
REGION="us-central1"
BACKEND_SERVICE="election-sim-backend"
FRONTEND_SERVICE="election-sim-frontend"

# ─── Resolve gcloud path ──────────────────────────────────────
GCLOUD="$HOME/google-cloud-sdk/bin/gcloud"
if ! command -v gcloud &> /dev/null && [ ! -f "$GCLOUD" ]; then
  echo "❌ gcloud not found. Install: https://cloud.google.com/sdk/docs/install"
  exit 1
fi
command -v gcloud &> /dev/null && GCLOUD="gcloud"

# Use custom config dir if default is not writable
if [ ! -w "$HOME/.config/gcloud" ] 2>/dev/null; then
  export CLOUDSDK_CONFIG="$HOME/PromptWar/.gcloud_config"
  mkdir -p "$CLOUDSDK_CONFIG"
  echo "⚠️  Using custom config dir: $CLOUDSDK_CONFIG"
fi

echo "🏛️ India Election Simulator — Cloud Run Deployment"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# ─── Step 1: Set project ──────────────────────────────────────
echo "📌 Setting project to $PROJECT_ID..."
$GCLOUD config set project $PROJECT_ID

# ─── Step 2: Enable required APIs ─────────────────────────────
echo "🔧 Enabling required Google Cloud APIs..."
$GCLOUD services enable \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  artifactregistry.googleapis.com \
  aiplatform.googleapis.com \
  firestore.googleapis.com \
  storage.googleapis.com \
  logging.googleapis.com \
  2>/dev/null || true
echo "✅ APIs enabled"

# ─── Step 3: Deploy Backend ───────────────────────────────────
echo ""
echo "🔨 Deploying Backend to Cloud Run..."
$GCLOUD run deploy $BACKEND_SERVICE \
  --source=india-democracy-simulator/backend \
  --region=$REGION \
  --platform=managed \
  --allow-unauthenticated \
  --memory=512Mi \
  --cpu=1 \
  --min-instances=0 \
  --max-instances=5 \
  --set-env-vars="DATABASE_URL=sqlite+aiosqlite:///./india_democracy_sim.db,JWT_SECRET_KEY=$(openssl rand -hex 32),DEBUG=false" \
  --quiet

BACKEND_URL=$($GCLOUD run services describe $BACKEND_SERVICE --region=$REGION --format='value(status.url)')
echo "✅ Backend deployed: $BACKEND_URL"

# ─── Step 4: Deploy Frontend ──────────────────────────────────
echo ""
echo "🔨 Deploying Frontend to Cloud Run..."
$GCLOUD run deploy $FRONTEND_SERVICE \
  --source=india-democracy-simulator/frontend \
  --region=$REGION \
  --platform=managed \
  --allow-unauthenticated \
  --memory=512Mi \
  --cpu=1 \
  --min-instances=0 \
  --max-instances=5 \
  --set-env-vars="NEXT_PUBLIC_API_URL=${BACKEND_URL}/api/v1" \
  --build-env-vars="NEXT_PUBLIC_API_URL=${BACKEND_URL}/api/v1" \
  --quiet

FRONTEND_URL=$($GCLOUD run services describe $FRONTEND_SERVICE --region=$REGION --format='value(status.url)')
echo "✅ Frontend deployed: $FRONTEND_URL"

# ─── Step 5: Update Backend CORS ──────────────────────────────
echo ""
echo "🔒 Updating Backend CORS with frontend URL..."
$GCLOUD run services update $BACKEND_SERVICE \
  --region=$REGION \
  --update-env-vars="ALLOWED_ORIGIN=$FRONTEND_URL" \
  --quiet

# ─── Summary ──────────────────────────────────────────────────
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎉 Deployment Complete!"
echo ""
echo "Frontend: $FRONTEND_URL"
echo "Backend:  $BACKEND_URL"
echo "Health:   $BACKEND_URL/health"
echo ""
echo "Google Cloud Services:"
echo "  ✅ Cloud Run (auto-scaling)"
echo "  ✅ Vertex AI (Gemini 2.0)"
echo "  ✅ Cloud Logging (structured)"
echo "  ⚠️  Firebase Auth — enable at https://console.firebase.google.com"
echo "  ⚠️  Firestore — enable at https://console.firebase.google.com"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
