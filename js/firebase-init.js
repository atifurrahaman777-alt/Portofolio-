const firebaseConfig = {
  apiKey: "AIzaSyArfUhdOVfyIsjKjfD_9BkbixxNa6XRvsM",
  authDomain: "manz-web.firebaseapp.com",
  projectId: "manz-web",
  storageBucket: "manz-web.firebasestorage.app",
  messagingSenderId: "178479215158",
  appId: "1:178479215158:web:265819c21836b2116f5e97"
};
firebase.initializeApp(firebaseConfig);
const auth = firebase.auth();
const db = firebase.firestore();
