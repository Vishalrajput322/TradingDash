import 'package:flutter/material.dart';

class AppTheme {
  static const Color background = Color(0xFF0B0E14);
  static const Color surface = Color(0xFF151A24);
  static const Color border = Color(0xFF232B3A);
  static const Color bullish = Color(0xFF00C853);
  static const Color bearish = Color(0xFFFF3D00);
  static const Color neutral = Color(0xFFFFB300);

  static ThemeData get darkTheme {
    return ThemeData.dark().copyWith(
      scaffoldBackgroundColor: background,
      cardColor: surface,
      appBarTheme: const AppBarTheme(
        backgroundColor: background,
        elevation: 0,
        centerTitle: false,
      ),
      colorScheme: const ColorScheme.dark(
        primary: Color(0xFF3B82F6),
        surface: surface,
      ),
    );
  }
}
