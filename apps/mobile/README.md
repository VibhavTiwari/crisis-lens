# CrisisLens Mobile App

React Native mobile application for iOS and Android crisis monitoring.

## Features

✅ **Authentication**
- Email/password login
- Biometric authentication (Face ID, Touch ID, Fingerprint)
- Secure token storage with SecureStore

✅ **Push Notifications**
- Firebase Cloud Messaging integration
- Local notifications
- Background notification handling

✅ **Offline Support**
- AsyncStorage data caching
- Sync queue for offline actions
- Network status monitoring

✅ **Core Features**
- Crisis item feed with infinite scroll
- Search and filtering
- Item details and claim verification
- Camera integration for evidence upload
- Map view with geolocation

## Setup

```bash
cd apps/mobile

# Install dependencies
npm install

# Start development server
npm start

# Run on iOS
npm run ios

# Run on Android
npm run android
```

## Configuration

1. **API URL** - Update in `app.json`:
```json
"extra": {
  "apiUrl": "https://your-api-url.com"
}
```

2. **Firebase** - Add `google-services.json` (Android) and `GoogleService-Info.plist` (iOS)

3. **Google Maps API Key** - Update in `app.json`

## Building for Production

```bash
# Install EAS CLI
npm install -g eas-cli

# Configure EAS
eas build:configure

# Build for iOS
eas build --platform ios

# Build for Android
eas build --platform android
```

## File Structure

```
src/
├── contexts/       # React contexts (Auth)
├── services/       # API, Camera, Location, Notifications, Offline
├── screens/        # App screens
├── navigation/     # Navigation configuration
├── components/     # Reusable components
├── hooks/          # Custom React hooks
└── utils/          # Utility functions
```

## Permissions

- Camera - For capturing crisis evidence
- Location - For tagging crisis events
- Notifications - For push alerts
- Biometrics - For secure authentication

## Tech Stack

- React Native 0.73
- Expo SDK 50
- TypeScript
- React Navigation
- React Query
- Zustand (state management)
