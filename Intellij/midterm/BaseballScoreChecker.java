package quiz;

public class BaseballScoreChecker {
    // 定義最大局數
    private static final int MAX_INNINGS = 12;
    // 陣列大小：[隊伍數][最大局數 + 1 (總分)]
    // index 0: 總分 (Total)
    // index 1-12: 第 1 到 12 局分數 (Innings)
    private static final int ARRAY_SIZE = MAX_INNINGS + 1;

    /**
     * 檢查並驗證比賽成績。
     *
     * @param score 包含兩隊分數的二維陣列。score[0] 隊伍A (先攻)，score[1] 隊伍B (後攻)。
     * 每個子陣列的 index 0 應為總分 (但會被重新計算和驗證)，index 1 到 N 為單局分數。
     * 若某局下半場未進行，則分數應為 -1。
     * @return 處理後的分數陣列 (包含正確的總分)。
     */
    public static int[][] checkScore(int[][] score)  {
        // 使用 assert 進行基本輸入檢查
        assert score != null : "分數陣列不能為空 (Null Score Array)";
        assert score.length == 2 : "必須提供兩隊 (A 和 B) 的分數 (Two teams required)";

        // 複製一份結果陣列，確保 index 0 的總分計算正確，並進行驗證
        int[][] resultScore = new int[2][ARRAY_SIZE];
        int currentInning = 0;
        int teamATotal = 0;
        int teamBTotal = 0;
        boolean gameEnded = false; // 標記比賽是否已根據規則結束

        System.out.println("--- 開始處理新的比分表 ---");
        //** LOG INFO

        // 1. 遍歷局數，計算分數並檢查規則
        for (int i = 1; i <= MAX_INNINGS; i++) {
            if (i >= score[0].length || i >= score[1].length) {
                // 如果已經讀完提供的資料，則跳出迴圈
                break;
            }

            currentInning = i;
            int scoreA = score[0][i];
            int scoreB = score[1][i];

            // 異常分數超出範圍檢查 (假設單局分數合理範圍是 0-99)
            if (scoreA < -1 || scoreA > 99 || scoreB < -1 || scoreB > 99) {
                System.out.println("異常分數超出範圍: 第 " + i + " 局的得分必須介於 0 到 99 之間 (或 -1 表示未進行下半局)。");
                //** LOG WARN and throw GameException
            }

            // 異常末局分數檢查：-1 只能用於後攻隊伍 (B)
            if (scoreA == -1) {
                System.out.println("異常末局分數: 先攻隊伍 (A) 的分數不能為 -1。");
                //** LOG WARN and throw GameException

            }

            // 累積總分 (忽略 -1)
            teamATotal += scoreA;
            if (scoreB != -1) {
                teamBTotal += scoreB;
            }

            resultScore[0][i] = scoreA;
            resultScore[1][i] = scoreB;

            // 2. 檢查提前結束規則
            if (!gameEnded) {
                // 規則 A: 第 7 局後 (含)，相差 10 分，提前結束 (Run-Ahead Rule)
                if (i >= 7 && Math.abs(teamATotal - teamBTotal) >= 10) {
                    gameEnded = true;
                    System.out.println("比賽於第 " + i + " 局結束 (分差 >= 10)。");
                    //** LOG INFO

                    // 檢查提前結束時的分數是否合乎邏輯
                    if (teamATotal < teamBTotal && scoreB == -1) {
                        // B 贏，且 B 的下半場未打，這是正常的
                        System.out.println("隊伍B獲勝，第 " + i + " 局下半場未進行 (X)。");
                        //** LOG INFO

                    } else if (teamATotal == teamBTotal && scoreB == -1) {
                        // 平手，且 B 的下半場未打，這是異常的
                        System.out.println("異常的提前結束: 提前結束時比分平手，且 B 隊的下半場未進行。");
                        //** LOG WARN and throw GameException


                    } else if (scoreB == -1 && teamATotal > teamBTotal) {
                        // A 贏，且 B 的下半場未打，但 B 隊應該有機會追分，這是不合理的。
                        System.out.println("異常的提前結束: 提前結束時 A 隊領先，且 B 隊的下半場未進行。");
                        //** LOG WARN and throw GameException


                    }

                    // 檢查後續局數是否為 0 或未提供
                    if ((i < score[0].length-1 && score[0][i+1] != 0) || (i < score[1].length-1 && score[1][i+1] != 0 && score[1][i+1] != -1)) {
                        System.out.println("異常的提前結束: 比賽已於第 " + i + " 局結束，但後續局數 (" + (i+1) + " 局) 仍有分數或標記。");
                        //** throw exception

                    }
                }

                // 規則 B: 檢查下半局提前結束 (Walk-off)
                if (i >= 9 && teamBTotal > teamATotal && scoreB == -1) {
                    // 隊伍B在正規/延長賽的下半場開始前或剛開始後領先，下半場不需要進行。
                    gameEnded = true;
                    System.out.println("異常的提前結束: 隊伍B在第 " + i + " 局下半場開始前獲勝，下半場分數為 -1 (X)。");
                    //** LOG INFO

                    // 檢查後續局數是否為 0 或未提供
                    if ((i < score[0].length-1 && score[0][i+1] != 0) || (i < score[1].length-1 && score[1][i+1] != 0 && score[1][i+1] != -1)) {
                        System.out.println("異常的提前結束: 比賽已於第 " + i + " 局結束，但後續局數 (" + (i+1) + " 局) 仍有分數或標記。");
                        //** throw GameException

                    }
                }
            } else {
                // 3. 檢查超過局數
                // 如果比賽已標記結束 (gameEnded=true)，則後續局數必須是 0 或 -1 (B隊)
                if (scoreA != 0 || (scoreB != 0 && scoreB != -1)) {
                    System.out.println("超過局數: 比賽已於第 " + (i - 1) + " 局結束，但第 " + i + " 局仍有分數。");
                    //** throw exception


                }
            }
        }

        // 4. 檢查比賽是否未結束
        if (!gameEnded) {
            if (currentInning < 9) {
                System.out.println("異常的未結束: 比賽不足九局。");
                //** throw exception


            } else if (currentInning == 9 && teamATotal == teamBTotal) {
                // 平手，應進入延長賽
                System.out.println("異常的未結束: 九局結束時平手，應進行延長賽至第 12 局。");
                //** throw exception


            } else if (currentInning > 9 && currentInning < MAX_INNINGS && teamATotal == teamBTotal) {
                // 延長賽中平手
                System.out.println("異常的未結束: 第 " + currentInning + " 局結束時平手，應繼續進行延長賽。");
                //** throw exception


            } else if (currentInning == MAX_INNINGS && teamATotal == teamBTotal) {
                // 12 局結束平手，這是正常的，比賽結束。
                System.out.println("比賽於第 12 局結束，比分為平手。");
                //** LOG INFO

                gameEnded = true;
            }
        }

        // 5. 將總分寫入 index 0
        resultScore[0][0] = teamATotal;
        resultScore[1][0] = teamBTotal;

        // 6. 決定最終結果訊息
        String outcome;
        if (resultScore[0][0] > resultScore[1][0]) {
            outcome = "隊伍A獲勝 (" + teamATotal + "-" + teamBTotal + ")";
        } else if (resultScore[1][0] > resultScore[0][0]) {
            outcome = "隊伍B獲勝 (" + teamBTotal + "-" + teamATotal + ")";
        } else {
            outcome = "平手 (" + teamATotal + "-" + teamBTotal + ")";
        }

        System.out.println("比分表處理完成。最終結果: " + outcome);
        // LOG INFO

        return resultScore;
    }

    /**
     * 將分數表輸出到控制台。
     * @param score 包含分數的二維陣列 (包含 index 0 的總分)。
     */
    public static void displayScores(int[][] score) {
        System.out.println("\n---------------------------------------------------");
        System.out.print("|   隊伍   | 總分 |");
        // 陣列大小可能比 MAX_INNINGS 小，所以這裡使用實際陣列長度
        int displayLength = Math.min(score[0].length, ARRAY_SIZE);
        for (int i = 1; i < displayLength; i++) {
            System.out.printf("%2d |", i);
        }
        System.out.println(" 狀態 |");
        System.out.println("---------------------------------------------------");

        String[] teamNames = {"A (先攻)", "B (後攻)"};

        for (int team = 0; team < 2; team++) {
            System.out.printf("| %s |%4d |", teamNames[team], score[team][0]);
            for (int i = 1; i < displayLength; i++) {
                int s = score[team][i];
                if (s == -1) {
                    System.out.print(" X |");
                } else {
                    System.out.printf("%2d |", s);
                }
            }

            String status = "";
            if (score[0][0] > score[1][0] && team == 0) { status = "獲勝"; }
            else if (score[1][0] > score[0][0] && team == 1) { status = "獲勝"; }
            else if (score[0][0] == score[1][0]) { status = "平手"; }

            System.out.printf(" %s |", status);
            System.out.println();
        }
        System.out.println("---------------------------------------------------");
    }

    /**
     * 主程式，包含測試案例。
     */
    public static void main(String[] args) {
        System.out.println("Log4j2 日誌系統已初始化 (依賴外部配置檔案)。");
        //** log info

        // 測試案例結構：[隊伍][局數]
        // 忽略 index 0 (總分)，從 index 1 (第 1 局) 開始

        // 1. 正常 9 局結束，A 隊獲勝 (15-10)
        int[][] case1 = {
                {0, 2, 1, 0, 3, 2, 1, 3, 3, 0}, // A: 總分 15
                {0, 1, 0, 2, 1, 0, 3, 1, 2, 0}  // B: 總分 10
        };

        // 2. 提前結束 (7 局後相差 >= 10 分) - B 隊 12-2 獲勝
        int[][] case2 = {
                {0, 0, 1, 0, 0, 1, 0, 0}, // A: 總分 2 (第 7 局上結束)
                {0, 2, 5, 0, 1, 0, 4, -1} // B: 總分 12 (第 7 局下 B 隊領先 10 分，下半場不需要打)
        };

        // 3. 延長賽 12 局結束，B 隊獲勝 (5-4)
        int[][] case3 = {
                {0, 0, 1, 0, 1, 0, 0, 0, 2, 0, 0, 0, 0}, // A: 總分 4 (第 12 局上)
                {0, 1, 0, 0, 1, 0, 1, 0, 1, 0, 0, 0, 1}  // B: 總分 5 (第 12 局下 B 得分後結束，下半場未標記-1是合理的，因為是Walk-off)
        };

        // 4. 9 局平手 (3-3)，應進入延長賽 (預期 GameException)
        int[][] case4 = {
                {0, 1, 0, 1, 0, 0, 0, 1, 0, 0}, // A: 總分 3
                {0, 0, 1, 0, 1, 0, 1, 0, 0, 0}  // B: 總分 3
        };

        // 5. 異常分數 (單局分數 100) (預期 GameException)
        int[][] case5 = {
                {0, 100, 1, 0, 0, 0, 0, 0, 0, 0}, // A: 總分 101
                {0, 0, 1, 0, 1, 0, 1, 0, 0, 0}    // B: 總分 3
        };

        // 6. 異常的提前結束
        int[][] case6 = {
                {0, 0, 1, 0, 1, 0, 1, 0, 1}, // A: 總分 4
                {0, 1, 0, 1, 0, 1, 0, 1, -1} // B: 第八局就以 -1 標記結束
        };

        // 7. 異常的未結束 - 九局已分勝負 (預期 GameException)
        int[][] case7 = {
                {0, 1, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0},
                {0, 0, 1, 0, 1, 0, 1, 0, 1, 1, 0, 0}
        };

        // 8. 異常的未結束
        int[][] case8 = {
                {0, 1, 0, 1, 0, 0, 0, 1, 0, 1, 0, 1, 0}, // A: 總分 5
                {0, 0, 1, 0, 1, 0, 1, 0, 1, 1, 0, 1, 0}  // B: 11 局已 6 分
        };


        int caseCount = 0;

        int[][][] testCases = {case1, case2, case3, case4, case5, case6, case7, case8};
        String[] caseDescriptions = {
                "1. 正常 9 局 A 獲勝 (15-10)",
                "2. 7 局提前結束 B 獲勝 (12-2, B下半場X)",
                "3. 12 局延長賽 B 獲勝 (5-4, 12局下Walk-off)",
                "4. 9 局平手 (3-3)，應進入延長賽 (預期 GameException)",
                "5. 異常分數 (單局分數 100) (預期 GameException)",
                "6. 異常的提前結束",
                "7. 異常的未結束 - 九局已分勝負 (預期 GameException)",
                "8. 異常的未結束 - 11 局已分勝負"
        };


        for (int i = 0; i < testCases.length; i++) {
            caseCount++;
            System.out.println("\n===== 測試案例" + caseDescriptions[i] + " =====");
            int[][] finalScore = checkScore(testCases[i]);

            displayScores(finalScore);
            //* exception handling and logging

        }
    }
}
