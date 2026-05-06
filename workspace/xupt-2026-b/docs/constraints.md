# B 题约束阈值记录

## 明文已知（docx 纯文本直读）

| 量 | 符号 | 值 |
|---|---|---|
| 定位方式 1 采样率 | fs_1 | 4 Hz（0.25 s） |
| 定位方式 2 采样率 | fs_2 | 5 Hz（0.2 s） |
| 输出轨迹采样率 | fs_out | 10 Hz |
| 单次射击命中率 | η_hit | 0.85 |
| 射击瞄准准备时长 | Δ_prep_shoot | 1.5 s |
| 拍照相机对准准备时长 | Δ_prep_photo | 0.5 s |

## 待填（从 `workspace/2026年西邮校赛赛题及相关材料/2026_B题/extracted_images/` 的 12 张 WMF 公式图中读出）

填写时直接替换下方 `?` 为实际数值。不确定下界上界时在旁边标注。

```yaml
# 射击任务约束
D_shoot_min: ?       # m
D_shoot_max: ?       # m
V_shoot_min: ?       # m/s
V_shoot_max: ?       # m/s
A_shoot_min: ?       # m/s^2
A_shoot_max: ?       # m/s^2

# 拍照任务约束
D_photo_min: ?       # m
D_photo_max: ?       # m
delta_theta_min: ?   # 度
V_photo_min: ?       # m/s
V_photo_max: ?       # m/s
A_photo_min: ?       # m/s^2
A_photo_max: ?       # m/s^2
```

## 语义决策（默认勾选项）

- [x] 同一射击目标至多射击 1 次
- [x] 任务时间窗禁止重叠：`[t − Δ_prep, t]` 两两不相交
- [x] 拍照同一目标的多次执行，两两方向角差 ≥ `delta_theta_min`
- [ ] 允许跨目标同时执行任务（N/A，单机器人）

## 图片索引（`extracted_images/imageN.wmf`）

12 张 wmf 依序对应（从 docx paragraph 16、18 的 OLE 引用顺序推测）：

| image # | 约束变量 | 含义 |
|---|---|---|
| 1, 2 | d 符号 + 射击距离范围 | d ∈ [?, ?] |
| 3, 4 | v 符号 + 射击速度范围 | v ∈ [?, ?] |
| 5, 6 | a 符号 + 射击加速度范围 | a ∈ [?, ?] |
| 7, 8 | d 符号 + 拍照距离范围 | d ∈ [?, ?] |
| 9 | 最小角差 | Δθ ≥ ? |
| 10, 11 | 拍照速度范围 | v ∈ [?, ?] |
| 12 | 拍照加速度范围 | a ∈ [?, ?] |

*注*：wmf 顺序可能与上表不完全对应；阅读时以双击图片看到的实际符号为准。
