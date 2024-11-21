from test_lexer import *
from test_parser import *
from custom_test_runner import CustomTestRunner, CustomTestResult
import sys
import unittest

if __name__ == '__main__':
    # Test cases
    test_cases = [TestLexerOperation, TestLexerTokens, TestParser]

    with open('tests/test_results.log', 'w') as log_file:
        # Run the tests
        for case in test_cases:
            suite = unittest.TestLoader().loadTestsFromTestCase(case)
            runner = CustomTestRunner(verbosity=0)
            result: CustomTestResult = runner.run(suite)

            log_file.write(f"{case.__name__}: {result.successes}/{result.testsRun} passed\n")
            for failure in result.failures:
                log_file.write(f"\n\tFAILURE: {failure[0]._testMethodName}\n\t\t")
                log_file.write('\n\t\t'.join(result.failures[0][1].strip().splitlines()[3:]) + '\n')

            log_file.write(f'\nRan {result.testsRun} tests in {result.stop_time - result.start_time:.3f}s\n')
            log_file.write(f'----------------------------------------------------------------------\n\n')
        log_file.flush()