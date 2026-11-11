export const Roles={admin:'质量负责人',analyst:'工艺分析师',viewer:'工艺观察员'} as const;
export const RunStatus={queued:'队列等待',running:'计算中',completed:'分析完成',failed:'计算失败'} as const;
export const ReviewStatus={submitted:'待复核',approved:'已批准',rejected:'退回调查'} as const;
export const SignalKinds={individual:'I 越界',moving_range:'MR 越界',ewma:'EWMA 越界'} as const;
