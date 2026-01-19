import 'dart:async';
import 'dart:convert';
import 'dart:io';
import 'dart:typed_data';

class SocketService {
  // ----------------- SINGLETON -----------------
  static final SocketService _instance = SocketService._internal();
  factory SocketService() => _instance;
  SocketService._internal();

  // ----------------- SOCKET -----------------
  Socket? _socket;
  int? userId;

  Completer<Map<String, dynamic>>? _pendingResponse;
  final StringBuffer _buffer = StringBuffer();

  // ----------------- CONFIG -----------------
  final String _host = '10.0.2.2'; // Android Emulator localhost
  final int _port = 5000;

  // ----------------- CONNECT -----------------
  Future<void> connect() async {
    if (_socket != null) return;

    _socket = await Socket.connect(
      _host,
      _port,
      timeout: const Duration(seconds: 5),
    );

    _socket!.setOption(SocketOption.tcpNoDelay, true);

    _socket!.listen(
      _onData,
      onError: _onError,
      onDone: _onDone,
      cancelOnError: true,
    );
  }

  // ----------------- DATA HANDLER -----------------
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
        _pendingResponse?.complete(decoded);
      } catch (e) {
        _pendingResponse?.completeError(e);
      } finally {
        _pendingResponse = null;
      }
    }
  }

  // ----------------- ERROR HANDLERS -----------------
  void _onError(Object error) {
    if (_pendingResponse != null && !_pendingResponse!.isCompleted) {
      _pendingResponse!.completeError(error);
    }
    _pendingResponse = null;
    _socket?.destroy();
    _socket = null;
  }

  void _onDone() {
    _socket?.destroy();
    _socket = null;
  }

  // ----------------- CORE SEND -----------------
  Future<Map<String, dynamic>> send(
    Map<String, dynamic> payload,
  ) async {
    await connect();

    if (_pendingResponse != null) {
      throw Exception("Another socket request is already in progress");
    }

    _pendingResponse = Completer<Map<String, dynamic>>();

    // 🔴 REQUIRED: newline-terminated JSON
    _socket!.write('${jsonEncode(payload)}\n');

    return _pendingResponse!.future.timeout(
      const Duration(seconds: 5),
      onTimeout: () {
        _pendingResponse = null;
        throw TimeoutException("Socket response timeout");
      },
    );
  }

  // ----------------- AUTH HELPERS -----------------
  void setUser(int id) {
    userId = id;
  }

  bool get isLoggedIn => userId != null;

  // ----------------- API METHODS -----------------
  Future<void> addExpense({
    required double amount,
    required String category,
    String note = "",
  }) async {
    if (userId == null) {
      throw Exception("User not logged in");
    }

    await send({
      "action": "add_expense",
      "user_id": userId,
      "amount": amount,
      "category": category,
      "note": note,
    });
  }

  Future<List<dynamic>> getExpenses() async {
    if (userId == null) {
      throw Exception("User not logged in");
    }

    final response = await send({
      "action": "get_expenses",
      "user_id": userId,
    });

    return (response["expenses"] ?? []) as List<dynamic>;
  }

  Future<double> getTotalExpense() async {
    if (userId == null) {
      throw Exception("User not logged in");
    }

    final response = await send({
      "action": "get_total",
      "user_id": userId,
    });

    return (response["total"] as num).toDouble();
  }

  // ----------------- CLEANUP -----------------
  void dispose() {
    _socket?.destroy();
    _socket = null;
    _pendingResponse = null;
    _buffer.clear();
    userId = null;
  }
}
