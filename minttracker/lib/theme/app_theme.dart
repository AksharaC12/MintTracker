import 'package:flutter/material.dart';

class AppTheme {
  static ThemeData lightTheme = ThemeData(
    scaffoldBackgroundColor: const Color(0xFFF5F5F0), // beige
    primaryColor: const Color(0xFF2E7D32), // green
    fontFamily: 'Roboto',

    appBarTheme: const AppBarTheme(
      backgroundColor: Color(0xFF2E7D32),
      foregroundColor: Colors.white,
      elevation: 0,
    ),

    bottomNavigationBarTheme: const BottomNavigationBarThemeData(
      backgroundColor: Colors.white,
      selectedItemColor: Color(0xFF2E7D32),
      unselectedItemColor: Colors.grey,
    ),

    cardTheme: CardTheme(
      color: Colors.white,
      elevation: 3,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
      ),
    ),
  );
}
