[
  {
    $addFields:
      /**
       * specifications: The fields to
       *   include or exclude.
       */
      {
        has_tones: "$tones.has_tones",
      },
  },
  {
    $match:
      /**
       * query: The query in MQL.
       */
      {
        has_tones: true,
        talkgroup_tag: "Westford Police",
        transcript: {$ne: null}
      },
  },
  {
    $project:
      /**
       * specifications: The fields to
       *   include or exclude.
       */
      {
        has_tones: 1,
        talkgroup_tag: 1,
        tones: 1,
        start_time: 1,
        transcript: "$transcript.transcript",
        quick_call: "$tones.quick_call",
        hi_low: "$tones.hi_low",
        long: "$tones.long",
      },
  },
  {
    $unwind:
      /**
       * path: Path to the array field.
       * includeArrayIndex: Optional name for index.
       * preserveNullAndEmptyArrays: Optional
       *   toggle to unwind null and empty values.
       */
      {
        path: "$quick_call",
        preserveNullAndEmptyArrays: true,
      },
  },
  {
    $unwind: {
      path: "$hi_low",
      preserveNullAndEmptyArrays: true,
    },
  },
  {
    $unwind: {
      path: "$long",
      preserveNullAndEmptyArrays: true,
    },
  },
]





[
  {
    $addFields: {
      has_tones: "$tones.has_tones",
    },
  },
  {
    $match:
      /**
       * query: The query in MQL.
       */
      {
        has_tones: true,
        transcript: {
          $ne: null,
        },
      },
  },
  {
    $unwind:
      /**
       * path: Path to the array field.
       * includeArrayIndex: Optional name for index.
       * preserveNullAndEmptyArrays: Optional
       *   toggle to unwind null and empty values.
       */
      {
        path: "$srcList",
        includeArrayIndex: "string",
        preserveNullAndEmptyArrays: true,
      },
  },
  {
    $project:
      /**
       * newField: The new field name.
       * expression: The new field expression.
       */
      {
        talkgroup_tag: 1,
        talkgroup: 1,
        source: "$srcList.src",
        source_tag: "$srcList.tag",
        start_time: 1,
        stop_time: 1,
        shortname: 1,
        filepath: 1,
        quick_call: "$tones.quick_call",
        hi_low: "$tones.hi_low",
        long: "$tones.long",
        transcript: "$transcript.transcript",
      },
  },
  {
    $unwind:
      /**
       * path: Path to the array field.
       * includeArrayIndex: Optional name for index.
       * preserveNullAndEmptyArrays: Optional
       *   toggle to unwind null and empty values.
       */
      {
        path: "$quick_call",
        preserveNullAndEmptyArrays: true,
      },
  },
  {
    $unwind: {
      path: "$hi_low",
      preserveNullAndEmptyArrays: true,
    },
  },
  {
    $unwind: {
      path: "$long",
      preserveNullAndEmptyArrays: true,
    },
  },
]