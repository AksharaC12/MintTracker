import 'package:flutter/material.dart';
import '../services/socket_service.dart';
import 'expenses_screen.dart';
import 'add_expense_screen.dart';

class DashboardScreen extends StatefulWidget {
  const DashboardScreen({super.key});

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  double total = 0.0;
  bool initialized = false;

  @override
  void initState() {
    super.initState();
    initDashboard();
  }

  /// Dashboard initialization
  /// Socket is already connected & registered in main.dart
  Future<void> initDashboard() async {
    await loadTotal();

    setState(() {
      initialized = true;
    });
  }

  Future<void> loadTotal() async {
    final value = await SocketService().getTotalExpense();
    setState(() {
      total = value;
    });
  }

  @override
  Widget build(BuildContext context) {
    if (!initialized) {
      return const Scaffold(
        body: Center(child: CircularProgressIndicator()),
      );
    }

    return Scaffold(
      appBar: AppBar(
        title: const Text("MintTracker"),
        centerTitle: true,
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text(
              "Total Spent",
              style: Theme.of(context).textTheme.titleLarge,
            ),
            const SizedBox(height: 8),
            Text(
              "₹${total.toStringAsFixed(2)}",
              style: const TextStyle(
                fontSize: 32,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 30),
            ElevatedButton(
              onPressed: () async {
                await Navigator.push(
                  context,
                  MaterialPageRoute(
                    builder: (_) => const ExpensesScreen(),
                  ),
                );
                loadTotal();
              },
              child: const Text("View Expenses"),
            ),
            const SizedBox(height: 12),
            ElevatedButton(
              onPressed: () async {
                await Navigator.push(
                  context,
                  MaterialPageRoute(
                    builder: (_) => const AddExpenseScreen(),
                  ),
                );
                loadTotal();
              },
              child: const Text("Add Expense"),
            ),
          ],
        ),
      ),
    );
  }
}
