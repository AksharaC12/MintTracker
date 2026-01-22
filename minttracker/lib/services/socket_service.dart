import 'dart:async';
import 'dart:convert';
import 'dart:io';
import 'dart:typed_data';

class SocketService {
  // 🔒 SINGLETON
  static final SocketService _instance = SocketService._internal();
  factory SocketService() => _instance;
  SocketService._internal();

  Socket? _socket;
  int? userId;

  Completer<Map<String, dynamic>>? _pending;
  final StringBuffer _buffer = StringBuffer();

  final String _host = '10.0.2.2';
  final int _port = 5000;

  bool _manuallyLoggedOut = false;

  // ---------- CONNECT ----------
  Future<void> connect() async {
    if (_socket != null) return;

    try {
      _socket = await Socket.connect(
        _host,
        _port,
        timeout: const Duration(seconds: 5),
      );

      _socket!.listen(
        _onData,
        onError: _onError,
        onDone: _onDone,
      );
    } catch (e) {
      throw Exception("Unable to connect to server");
    }
  }

  // ---------- RECEIVE ----------
  void _onData(Uint8List data) {
    _buffer.write(utf8.decode(data));

    while (_buffer.toString().contains('\n')) {
      final full = _buffer.toString();
      final index = full.indexOf('\n');

      final message = full.substring(0, index).trim();
      _buffer.clear();
      _buffer.write(full.substring(index + 1));

      if (message.isEmpty) continue;

      try {
        final decoded = jsonDecode(message) as Map<String, dynamic>;
        _pending?.complete(decoded);
      } catch (_) {
        _pending?.completeError("Invalid JSON from server");
      } finally {
        _pending = null;
      }
    }
  }

  void _onError(error) {
    _pending?.completeError(error);
    _pending = null;

    // ❌ DO NOT LOG OUT
    _socket = null;
  }

  void _onDone() {
    // ❌ DO NOT LOG OUT
    _socket = null;
  }

  // ---------- SEND ----------
  Future<Map<String, dynamic>> send(Map<String, dynamic> payload) async {
    await connect();

    if (_pending != null) {
      throw Exception("Another request already running");
    }

    _pending = Completer<Map<String, dynamic>>();
    _socket!.write('${jsonEncode(payload)}\n');

    return _pending!.future.timeout(
      const Duration(seconds: 8),
      onTimeout: () {
        _pending = null;
        throw TimeoutException("Server timeout");
      },
    );
  }

  // ---------- AUTH ----------
  Future<int> signup(String fullName, String email, String password) async {
    final res = await send({
      "action": "signup",
      "full_name": fullName,
      "email": email,
      "password": password,
    });

    if (res["status"] != "success") {
      throw Exception(res["message"]);
    }

    userId = res["user_id"];
    _manuallyLoggedOut = false;
    return userId!;
  }

  Future<int> login(String email, String password) async {
    final res = await send({
      "action": "login",
      "email": email,
      "password": password,
    });

    if (res["status"] != "success") {
      throw Exception(res["message"]);
    }

    userId = res["user_id"];
    _manuallyLoggedOut = false;
    return userId!;
  }

  bool get isLoggedIn => userId != null;

  // ---------- EXPENSE ----------
  Future<Map<String, dynamic>> addExpense({
    required double amount,
    required String category,
    required String note,
    required DateTime date,
  }) async {
    if (userId == null) {
      throw Exception("User not logged in");
    }

    final res = await send({
      "action": "add_expense",
      "user_id": userId,
      "amount": amount,
      "category": category,
      "note": note,
      "date": date.toIso8601String().split("T").first,
    });

    if (res["status"] != "success") {
      throw Exception(res["message"]);
    }

    return res;
  }

  Future<List<dynamic>> getExpenses() async {
    if (userId == null) return [];

    final res = await send({
      "action": "get_expenses",
      "user_id": userId,
    });

    if (res["status"] != "success") {
      throw Exception(res["message"]);
    }

    return res["data"] as List<dynamic>;
  }

  Future<double> getTotalExpense() async {
    if (userId == null) return 0;

    final res = await send({
      "action": "get_total",
      "user_id": userId,
    });

    return (res["total"] as num).toDouble();
  }

  Future<Map<String, double>> getCategorySummary() async {
    if (userId == null) return {};

    final res = await send({
      "action": "category_summary",
      "user_id": userId,
    });

    final Map<String, double> result = {};
    for (final row in res["data"]) {
      result[row["category_name"]] = (row["total"] as num).toDouble();
    }

    return result;
  }

  // ---------- LOGOUT ----------
  void logout() {
    _manuallyLoggedOut = true;
    userId = null;
    dispose();
  }

  // ---------- CLEANUP ----------
  void dispose() {
    try {
      _socket?.destroy();
    } catch (_) {}
    _socket = null;
    _pending = null;
    _buffer.clear();
  }
}
