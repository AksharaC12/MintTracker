import 'package:flutter/material.dart';
import '../services/socket_service.dart';

class ExpensesScreen extends StatefulWidget {
  const ExpensesScreen({super.key});

  @override
  State<ExpensesScreen> createState() => _ExpensesScreenState();
}

class _ExpensesScreenState extends State<ExpensesScreen> {
  List expenses = [];
  bool loading = true;

  @override
  void initState() {
    super.initState();
    loadExpenses();
  }

  Future<void> loadExpenses() async {
    final data = await SocketService().getExpenses();
    setState(() {
      expenses = data;
      loading = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Expenses")),
      body: loading
          ? const Center(child: CircularProgressIndicator())
          : expenses.isEmpty
              ? const Center(child: Text("No expenses yet"))
              : ListView.builder(
                  itemCount: expenses.length,
                  itemBuilder: (_, i) {
                    final e = expenses[i];
                    return Card(
                      margin: const EdgeInsets.symmetric(
                        horizontal: 12,
                        vertical: 6,
                      ),
                      child: ListTile(
                        title: Text(e["category"]),
                        subtitle: Text(e["note"] ?? ""),
                        trailing: Text("₹${e["amount"]}"),
                      ),
                    );
                  },
                ),
    );
  }
}
