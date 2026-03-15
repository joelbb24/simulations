import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:google_fonts/google_fonts.dart';
import 'package:animate_do/animate_do.dart';

void main() => runApp(const StoicApp());

class StoicApp extends StatelessWidget {
  const StoicApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Stoic Quotes',
      debugShowCheckedModeBanner: false,
      theme: ThemeData.dark().copyWith(
        scaffoldBackgroundColor: const Color(0xFF0D0D0D),
      ),
      home: const QuotePage(),
    );
  }
}

class QuotePage extends StatefulWidget {
  const QuotePage({super.key});

  @override
  State<QuotePage> createState() => _QuotePageState();
}

class _QuotePageState extends State<QuotePage> {
  String _quote = '';
  String _author = '';
  bool _loading = true;
  int _animKey = 0;

  // Change this to your machine's IP if running on a physical device
  static const String _apiUrl = 'http://localhost:8000/quote';

  @override
  void initState() {
    super.initState();
    _fetchQuote();
  }

  Future<void> _fetchQuote() async {
    setState(() {
      _loading = true;
      _quote = '';
      _author = '';
    });

    try {
      final res = await http.get(Uri.parse(_apiUrl));
      if (res.statusCode == 200) {
        final data = jsonDecode(res.body);
        setState(() {
          _quote = data['text'];
          _author = data['author'];
          _loading = false;
          _animKey++;
        });
      }
    } catch (_) {
      setState(() {
        _quote = 'Could not reach the server.';
        _author = '';
        _loading = false;
        _animKey++;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            colors: [Color(0xFF0D0D0D), Color(0xFF1A1A2E), Color(0xFF16213E)],
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
          ),
        ),
        child: SafeArea(
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 48),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Header
                FadeInDown(
                  child: Text(
                    'STOIC\nWISDOM',
                    style: GoogleFonts.cormorantGaramond(
                      fontSize: 48,
                      fontWeight: FontWeight.w300,
                      color: Colors.white,
                      letterSpacing: 8,
                      height: 1.1,
                    ),
                  ),
                ),

                // Quote block
                Expanded(
                  child: Center(
                    child: _loading
                        ? const CircularProgressIndicator(
                            color: Color(0xFFD4AF37),
                          )
                        : FadeIn(
                            key: ValueKey(_animKey),
                            duration: const Duration(milliseconds: 800),
                            child: Column(
                              mainAxisSize: MainAxisSize.min,
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                // Decorative line
                                Container(
                                  width: 48,
                                  height: 2,
                                  color: const Color(0xFFD4AF37),
                                  margin: const EdgeInsets.only(bottom: 28),
                                ),
                                Text(
                                  '\u201C$_quote\u201D',
                                  style: GoogleFonts.cormorantGaramond(
                                    fontSize: 24,
                                    fontStyle: FontStyle.italic,
                                    color: Colors.white.withOpacity(0.92),
                                    height: 1.7,
                                    letterSpacing: 0.5,
                                  ),
                                ),
                                if (_author.isNotEmpty) ...[
                                  const SizedBox(height: 28),
                                  Text(
                                    '— $_author',
                                    style: GoogleFonts.cormorantGaramond(
                                      fontSize: 16,
                                      color: const Color(0xFFD4AF37),
                                      letterSpacing: 3,
                                      fontWeight: FontWeight.w600,
                                    ),
                                  ),
                                ],
                              ],
                            ),
                          ),
                  ),
                ),

                // Button
                FadeInUp(
                  child: GestureDetector(
                    onTap: _fetchQuote,
                    child: Container(
                      width: double.infinity,
                      padding: const EdgeInsets.symmetric(vertical: 18),
                      decoration: BoxDecoration(
                        border: Border.all(color: const Color(0xFFD4AF37), width: 1),
                        borderRadius: BorderRadius.circular(2),
                      ),
                      child: Text(
                        'NEW WISDOM',
                        textAlign: TextAlign.center,
                        style: GoogleFonts.cormorantGaramond(
                          fontSize: 14,
                          letterSpacing: 6,
                          color: const Color(0xFFD4AF37),
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
