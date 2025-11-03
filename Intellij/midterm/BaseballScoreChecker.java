package quiz;

import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import org.apache.logging.log4j.core.config.Configurator;
import org.apache.logging.log4j.core.config.builder.api.*;
import org.apache.logging.log4j.core.config.builder.impl.BuiltConfiguration;

import java.util.Arrays;

public class BaseballScoreChecker {

    // ===== 常數 =====
    private static final int MAX_INNINGS = 12;          // 最多 12 局
    private static final int ARRAY_SIZE  = MAX_INNINGS + 1; // [0]=總分, [1..12]=各局

    // ===== Logger：程式內建 Log4j2 設定（無外部檔）=====
    private static final Logger log = LogManager.getLogger(BaseballScoreChecker.class);

    static {
        // 程式啟動時，建立「寫檔 + 主控台」的 log4j2 設定，檔名 baseball.log
        ConfigurationBuilder<BuiltConfiguration> b = ConfigurationBuilderFactory.newConfigurationBuilder();
        b.setStatusLevel(org.apache.logging.log4j.Level.WARN);
        b.setConfigurationName("baseball-config");

        LayoutComponentBuilder layout = b.newLayout("PatternLayout")
                .addAttribute("pattern", "%d{yyyy-MM-dd HH:mm:ss.SSS} [%-5level] %c{1} - %msg%n");

        // 檔案 appender
        AppenderComponentBuilder file = b.newAppender("File", "File")
                .addAttribute("fileName", "baseball.log")
                .addAttribute("append", true)
                .add(layout);
        b.add(file);

        // 主控台 appender
        AppenderComponentBuilder console = b.newAppender("Console", "Console").add(layout);
        b.add(console);

        // 根 logger
        b.add(b.newRootLogger(org.apache.logging.log4j.Level.INFO)
                .add(b.newAppenderRef("Console"))
                .add(b.newAppenderRef("File")));

        Configurator.initialize(b.build());
        log.info("Log4j2 內建設定完成，寫入檔案：baseball.log");
    }

    // ===== 自訂例外 =====
    public static class GameException extends RuntimeException {
        public GameException(String message) { super(message); }
    }

    /**
     * 核心檢查（同時回填總分）
     */
    public static int[][] checkScore(int[][] score) {
        assert score != null : "Score array must not be null";
        assert score.length == 2 : "Must provide two teams";

        // 只複製到我們的標準大小（避免 display 誤導）
        int[][] result = new int[2][ARRAY_SIZE];
        int teamATotal = 0, teamBTotal = 0;
        int lastSeenInning = 0;
        boolean gameEnded = false;

        log.info("--- 開始檢查比分 ---");
        for (int i = 1; i <= MAX_INNINGS; i++) {
            // 若來源陣列沒提供到這一局，就停
            if (i >= score[0].length || i >= score[1].length) break;

            lastSeenInning = i;
            int a = score[0][i];
            int b = score[1][i];

            // 檢查單局分數：0..99；B 隊允許 -1（下半未打顯示 X）
            if (a < 0 || a > 99) {
                log.warn("異常分數超出範圍：第 {} 局 A={}", i, a);
                throw new GameException("異常分數超出範圍：第 " + i + " 局 A=" + a);
            }
            if (b < -1 || b > 99) {
                log.warn("異常分數超出範圍：第 {} 局 B={}", i, b);
                throw new GameException("異常分數超出範圍：第 " + i + " 局 B=" + b);
            }
            if (a == -1) {
                log.warn("異常末局分數：先攻 A 不允許 -1（X）於第 {} 局", i);
                throw new GameException("異常末局分數：A 不允許 -1（X）於第 " + i + " 局");
            }

            // 回填與累計（B=-1 不計總分）
            result[0][i] = a;
            result[1][i] = b;
            teamATotal += a;
            if (b != -1) teamBTotal += b;

            // 規則：第 7 局含之後分差 >=10，提前結束
            if (!gameEnded && i >= 7 && Math.abs(teamATotal - teamBTotal) >= 10) {
                gameEnded = true;
                log.info("第 {} 局觸發提前結束（分差 >=10）", i);

                // 合理性檢查
                if (teamATotal > teamBTotal && b == -1) {
                    // A 領先，但 B 下半未進行 → 應該要打完 B 的下半才能確定，不合理
                    log.warn("異常的提前結束：A 領先但 B 下半未進行（第 {} 局）", i);
                    throw new GameException("異常的提前結束：A 領先但 B 下半未進行（第 " + i + " 局）");
                }
                if (teamATotal == teamBTotal && b == -1) {
                    log.warn("異常的提前結束：分數平手卻標記 B=-1（第 {} 局）", i);
                    throw new GameException("異常的提前結束：分數平手卻標記 B=-1（第 " + i + " 局）");
                }

                // 比賽一旦結束：來源陣列不應再有 **任何後續局欄位**
                // （修 case7/8：避免「多餘局數」）
                if (score[0].length - 1 > i || score[1].length - 1 > i) {
                    log.warn("超過局數：比賽已於第 {} 局結束，但輸入仍包含後續局欄位", i);
                    throw new GameException("超過局數：第 " + i + " 局已結束，卻仍提供第 " + (i + 1) + " 局之後的欄位");
                }
                break; // 停止讀取更多局
            }

            // 規則：Walk-off（第 9 局含之後），若 B 在該局下半**未進行**（b=-1）且總分已領先 → 合法結束
            if (!gameEnded && i >= 9 && b == -1 && teamBTotal > teamATotal) {
                gameEnded = true;
                log.info("第 {} 局出現 Walk-off（B 已領先且下半不須進行）", i);

                if (score[0].length - 1 > i || score[1].length - 1 > i) {
                    log.warn("超過局數：Walk-off 於第 {} 局成立，但仍提供後續局欄位", i);
                    throw new GameException("超過局數：Walk-off 於第 " + i + " 局成立，卻仍提供後續局欄位");
                }
                break;
            }
        }

        // 若還沒結束，做結束條件檢查
        if (!gameEnded) {
            if (lastSeenInning < 9) {
                log.warn("異常的未結束：不足 9 局資料");
                throw new GameException("異常的未結束：不足 9 局");
            }
            if (lastSeenInning == 9 && teamATotal == teamBTotal) {
                log.warn("異常的未結束：9 局平手應進入延長賽");
                throw new GameException("異常的未結束：9 局平手應進入延長賽");
            }
            if (lastSeenInning > 9 && lastSeenInning < MAX_INNINGS && teamATotal == teamBTotal) {
                log.warn("異常的未結束：第 {} 局平手仍應繼續", lastSeenInning);
                throw new GameException("異常的未結束：第 " + lastSeenInning + " 局平手仍應繼續");
            }
            if (lastSeenInning == MAX_INNINGS && teamATotal == teamBTotal) {
                // 12 局平手 → 合法結束
                gameEnded = true;
                log.info("12 局結束，雙方平手");
            }
        }

        // 回填總分
        result[0][0] = teamATotal;
        result[1][0] = teamBTotal;

        // 只在「合法終局」時才產出勝負訊息（修 case5）
        if (!gameEnded) {
            log.warn("異常的未結束：輸入未達成任何合法終局條件");
            throw new GameException("異常的未結束：未達成合法終局條件");
        } else {
            if (teamATotal > teamBTotal) log.info("最終結果：A 勝 {}-{}", teamATotal, teamBTotal);
            else if (teamBTotal > teamATotal) log.info("最終結果：B 勝 {}-{}", teamBTotal, teamATotal);
            else log.info("最終結果：平手 {}-{}", teamATotal, teamBTotal);
        }

        return result;
    }

    /**
     * 只顯示「實際進行到的最後一局」，不再固定 12 局（修正誤導）
     */
    public static void displayScores(int[][] score) {
        // 推算要顯示到第幾局：找到最後一個「非 0 或 -1」的欄位；另考慮 -1 的 X 也要顯示
        int lastToShow = 1;
        for (int i = 1; i < Math.min(score[0].length, ARRAY_SIZE); i++) {
            if (score[0][i] != 0 || score[1][i] != 0 || score[1][i] == -1) lastToShow = i;
        }

        System.out.println("\n---------------------------------------------------");
        System.out.print("|   隊伍   | 總分 |");
        for (int i = 1; i <= lastToShow; i++) System.out.printf("%2d |", i);
        System.out.println(" 狀態 |");
        System.out.println("---------------------------------------------------");

        String[] teamNames = {"A (先攻)", "B (後攻)"};
        for (int t = 0; t < 2; t++) {
            System.out.printf("| %s |%4d |", teamNames[t], score[t][0]);
            for (int i = 1; i <= lastToShow; i++) {
                int s = score[t][i];
                if (s == -1) System.out.print(" X |");
                else System.out.printf("%2d |", s);
            }
            String status = "";
            if (score[0][0] > score[1][0] && t == 0) status = "獲勝";
            else if (score[1][0] > score[0][0] && t == 1) status = "獲勝";
            else if (score[0][0] == score[1][0]) status = "平手";
            System.out.printf(" %s |%n", status);
        }
        System.out.println("---------------------------------------------------");
    }

    public static void main(String[] args) {
        log.info("Log4j2 日誌系統已初始化（程式內建設定，無外部檔）。");

        // 以下測資沿用你題目的格式與內容
        int[][] case1 = {
                {0, 2, 1, 0, 3, 2, 1, 3, 3, 0},
                {0, 1, 0, 2, 1, 0, 3, 1, 2, 0}
        };

        int[][] case2 = {
                {0, 0, 1, 0, 0, 1, 0, 0},
                {0, 2, 5, 0, 1, 0, 4, -1}
        };

        int[][] case3 = {
                {0, 0, 1, 0, 1, 0, 0, 0, 2, 0, 0, 0, 0},
                {0, 1, 0, 0, 1, 0, 1, 0, 1, 0, 0, 0, 1}
        };

        int[][] case4 = {
                {0, 1, 0, 1, 0, 0, 0, 1, 0, 0},
                {0, 0, 1, 0, 1, 0, 1, 0, 0, 0}
        };

        int[][] case5 = {
                {0, 100, 1, 0, 0, 0, 0, 0, 0, 0},
                {0, 0, 1, 0, 1, 0, 1, 0, 0, 0}
        };

        int[][] case6 = {
                {0, 0, 1, 0, 1, 0, 1, 0, 1},
                {0, 1, 0, 1, 0, 1, 0, 1, -1}
        };

        int[][] case7 = {
                {0, 1, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0},
                {0, 0, 1, 0, 1, 0, 1, 0, 1, 1, 0, 0}
        };

        int[][] case8 = {
                {0, 1, 0, 1, 0, 0, 0, 1, 0, 1, 0, 1, 0},
                {0, 0, 1, 0, 1, 0, 1, 0, 1, 1, 0, 1, 0}
        };

        int[][][] tests = {case1, case2, case3, case4, case5, case6, case7, case8};
        String[] names = {
                "1. 正常 9 局 A 勝 (15-10)",
                "2. 7 局提前結束 B 勝 (12-2, B 下半 X)",
                "3. 12 局延長賽 B 勝 (5-4, 12 局下 Walk-off)",
                "4. 9 局平手，應進延長（預期例外）",
                "5. 異常分數 100（預期例外）",
                "6. 異常的提前結束（預期例外）",
                "7. 9 局已分勝負卻仍有後續局（預期例外）",
                "8. 11 局已分勝負卻仍有後續局（預期例外）"
        };

        for (int i = 0; i < tests.length; i++) {
            System.out.println("\n===== 測試案例 " + names[i] + " =====");
            try {
                int[][] finalScore = checkScore(tests[i]);
                displayScores(finalScore); // 僅在無例外時顯示（修正 case5 行為）
            } catch (GameException ex) {
                log.error("資料異常：{}", ex.getMessage());
                System.out.println("[異常] " + ex.getMessage());
            }
        }
    }
}
