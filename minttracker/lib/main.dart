import 'package:flutter/material.dart';
import 'screens/splash_screen.dart';

void main() {
  runApp(const MintTrackerApp());
}

class MintTrackerApp extends StatelessWidget {
  const MintTrackerApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'MintTracker',
      home: const SplashScreen(),
    );
  }
}
